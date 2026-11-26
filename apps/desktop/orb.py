"""PT's floating Windows interface.

Run this file to create the orb and its sliding chat window. Messages are sent
to server.py at http://127.0.0.1:8000/chat, so that backend must be running
to receive an answer.

Reading order:
    background_brightness: reads screen colors for automatic contrast.
    make_draggable: handles mouse gestures.
    StatusIcon: plays the orb's image animation.
    main: creates widgets and connects their callbacks.

Tk owns the main thread. Mouse events, drawing, and timer callbacks run there.
The HTTP request uses a worker thread, which returns its result through a queue.
"""

import math
import re
from collections import deque
from difflib import SequenceMatcher
import subprocess
import ctypes  # Calls Windows APIs using Python's standard library.
from ctypes import wintypes
from pathlib import Path
from statistics import median
import tkinter as tk
import tkinter.font as tkfont
from time import perf_counter

import queue  # Safely carries replies from the HTTP thread to the UI thread.
import threading  # Keeps waiting for a reply from freezing the interface.
import requests  # Sends a message and selected agent to PT's local backend.

from piper import PiperVoice
if __package__:
    from .pt_speech import speak
else:
    from pt_speech import speak


# Windows treats this color as fully transparent; window alpha controls the rest.
TRANSPARENT = "#ff00ff"
PANEL = "#111111"
FIELD = PANEL
TEXT = "#eeeeee"
MUTED = "#c0c0c0"
# Theme names describe the desktop behind PT. The panel contrasts with it.
# muted is placeholder/disabled text; hover is the selected or hovered surface.
THEMES = {
    "light": {"panel": "#14171b", "text": "#f0f2f5", "muted": "#aeb6c0",
             "hover": "#30353c"},
    "dark": {"panel": "#edf0f3", "text": "#171d25", "muted": "#515e6c",
              "hover": "#d2d9e0"},
}


SOUND_LABEL = re.compile(
    r"(?:\[|\()\s*(?:clapping|applause|silence|no (?:sound|speech|noise)|"
    r"blank[_ ]audio|music(?: playing)?|background noise|laughter|inaudible)"
    r"\s*(?:\]|\))", re.IGNORECASE
)


def has_speech(text):
    return bool(re.search(r"[^\W_]", SOUND_LABEL.sub("", text)))


def is_playback_echo(text, heard_at, recent_playback):
    def words(value):
        return re.findall(r"\w+", SOUND_LABEL.sub("", value).casefold().replace("jah", "ja"))

    heard = words(text)
    if not heard:
        return False
    for reply, start, end in recent_playback:
        # Whisper emits a segment after the sound and a pause.
        if not start <= heard_at <= end + 5:
            continue
        spoken = words(reply)
        for i in range(len(spoken)):
            fragment = spoken[i:i + len(heard)]
            if heard == fragment:
                return True
            if len(heard) >= 5 and SequenceMatcher(None, heard, fragment).ratio() >= 0.88:
                return True
    return False


def listening_context():
    """Return a coarse desktop hint when Whisper delivers a segment."""
    user32 = ctypes.windll.user32
    user32.GetForegroundWindow.restype = wintypes.HWND
    title = ctypes.create_unicode_buffer(1024)
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW(user32.GetForegroundWindow(), title, len(title))
    if "youtube" in title.value.casefold():
        return "youtube"
    state = ctypes.c_int()
    if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(state)) == 0:
        # QUNS_RUNNING_D3D_FULL_SCREEN.
        if state.value == 3:
            return "direct3d_fullscreen"
    return "unknown"


def background_brightness(windows):
    """Sample nearby desktop pixels outside PT's visible windows on Windows."""
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    # Declare native argument and return types, including full-size handles on
    # 64-bit Windows. GetDC acquires a screen drawing context; GetPixel reads it.
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user32.ReleaseDC.restype = ctypes.c_int
    gdi32.GetPixel.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.GetPixel.restype = wintypes.DWORD
    # Measure only mapped (currently visible) windows in desktop coordinates.
    bounds = [(w.winfo_rootx(), w.winfo_rooty(),
               w.winfo_rootx() + w.winfo_width(),
               w.winfo_rooty() + w.winfo_height())
              for w in windows if w.winfo_ismapped()]
    # Virtual desktop bounds include monitors with negative screen coordinates.
    left, top = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
    right = left + user32.GetSystemMetrics(78)
    bottom = top + user32.GetSystemMetrics(79)
    dc = user32.GetDC(None)
    if not dc:
        return None
    samples = []
    try:
        for x1, y1, x2, y2 in bounds:
            points = []
            # Sample three positions along each edge, 12 pixels outside the UI.
            # This approximates the background without reading our own colors.
            for fraction in (0.2, 0.5, 0.8):
                x = round(x1 + (x2 - x1) * fraction)
                y = round(y1 + (y2 - y1) * fraction)
                points.extend(((x, y1 - 12), (x, y2 + 12),
                               (x1 - 12, y), (x2 + 12, y)))
            for x, y in points:
                # Skip positions beyond the desktop or inside either PT window.
                if not (left <= x < right and top <= y < bottom):
                    continue
                if any(a <= x < c and b <= y < d for a, b, c, d in bounds):
                    continue
                color = gdi32.GetPixel(dc, x, y)
                # Windows reports an unreadable pixel with this sentinel value.
                if color == 0xFFFFFFFF:
                    continue
                r, g, b = color & 255, (color >> 8) & 255, (color >> 16) & 255
                # COLORREF packs red into the lowest byte. Weight green most
                # heavily to estimate perceived brightness between zero and one.
                samples.append((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255)
    finally:
        # Always release the context, even if sampling raises an exception.
        user32.ReleaseDC(None, dc)
    # The median reduces the effect of individual bright details or text.
    return median(samples) if samples else None


def make_draggable(widget, window, on_click=None):
    """Move a window with this widget; optionally treat a short gesture as a click."""
    # Use screen coordinates so movement stays consistent as the window moves.
    start = None
    dragging = False

    def press(event):
        """Remember where the mouse and window were when the gesture began."""
        nonlocal start, dragging
        start = (event.x_root, event.y_root, window.winfo_x(), window.winfo_y())
        dragging = False

    def move(event):
        """Apply the mouse displacement to the original window position."""
        nonlocal dragging
        if start is None:
            return
        mouse_x, mouse_y, window_x, window_y = start
        dx, dy = event.x_root - mouse_x, event.y_root - mouse_y
        # Small movements still count as clicks and can toggle the chat panel.
        if dragging or math.hypot(dx, dy) >= 5:
            dragging = True
            window.geometry(f"+{window_x + dx}+{window_y + dy}")

    def release(_event):
        """Trigger the click action only when the gesture did not become a drag."""
        nonlocal start
        if start is not None and not dragging and on_click is not None:
            on_click()
        start = None

    widget.bind("<ButtonPress-1>", press)
    widget.bind("<B1-Motion>", move)
    widget.bind("<ButtonRelease-1>", release)


class StatusIcon:
    """Manual animation controls. Call these methods on the Tk UI thread."""

    def __init__(self, canvas):
        """Load the ring-to-character sprite strip and display its first frame."""
        self.canvas = canvas
        self.palettes = {}
        for backdrop, tone in (("dark", "pearl"), ("light", "ink")):
            path = Path(__file__).with_name("assets") / f"ring-rika-{tone}.png"
            sheet = tk.PhotoImage(master=canvas, file=str(path))
            frames = []
            for x in range(0, sheet.width(), 80):
                frame = tk.PhotoImage(master=canvas, width=80, height=80)
                frame.tk.call(str(frame), "copy", str(sheet), "-from", x, 0, x + 80, 80)
                frames.append(frame)
            self.palettes[backdrop] = frames
        self.frames = self.palettes["dark"]
        self.index = 0
        self.item = canvas.create_image(40, 40, image=self.frames[0])
        self.timer = None
        self.active = False

    def set_background(self, backdrop):
        """Switch ink while preserving the current sprite animation frame."""
        self.frames = self.palettes[backdrop]
        self.canvas.itemconfigure(self.item, image=self.frames[self.index])

    def transform_to_rika(self):
        """Start the transition once; repeated calls while active do nothing."""
        if not self.active:
            self.active = True
            self._play(1)

    def _play(self, index):
        """Display the next sprite frame, then start the idle breathing motion."""
        # Schedule frames on Tk's event loop so input and dragging stay responsive.
        self.index = index
        self.canvas.itemconfigure(self.item, image=self.frames[index])
        if index + 1 < len(self.frames):
            self.timer = self.canvas.after(160, self._play, index + 1)
        else:
            self._breathe(perf_counter())

    def _breathe(self, started):
        """Use elapsed time for a repeating five-second vertical motion."""
        # After the transition, gently move the final frame up and down.
        phase = (perf_counter() - started) * math.tau / 5
        self.canvas.coords(self.item, 40, 40 + math.sin(phase))
        self.timer = self.canvas.after(100, self._breathe, started)

    def return_to_ring(self):
        """Stop animation and restore the original ring image and position."""
        # Cancel the pending animation before restoring the idle frame.
        self.active = False
        if self.timer is not None:
            self.canvas.after_cancel(self.timer)
            self.timer = None
        self.canvas.coords(self.item, 40, 40)
        self.index = 0
        self.canvas.itemconfigure(self.item, image=self.frames[0])


def main():
    """Build the interface and start Tk's event loop."""
    # The borderless orb and chat are separate windows positioned together.
    orb = tk.Tk()
    orb.title("PT Orb")
    orb.overrideredirect(True)
    # Remove the native title bar; our drag handler supplies window movement.
    orb.attributes("-topmost", True)
    orb.attributes("-transparentcolor", TRANSPARENT)
    orb.attributes("-alpha", 0.52)
    # Alpha controls opacity: zero is invisible, one is fully opaque.
    size = 80
    orb.geometry(f"{size}x{size}+{max(0, orb.winfo_screenwidth() - 120)}+100")

    canvas = tk.Canvas(orb, bg=TRANSPARENT, highlightthickness=0, cursor="hand2")
    canvas.pack(fill="both", expand=True)
    orb.status_icon = StatusIcon(canvas)

    chat = tk.Toplevel(orb)
    chat.title("PT Chat")
    chat.withdraw()
    # Build the chat window while hidden. The orb's click callback reveals it.
    chat.overrideredirect(True)
    chat.attributes("-topmost", True)
    chat.attributes("-alpha", 0.61)
    chat.attributes("-transparentcolor", TRANSPARENT)
    chat.configure(bg=TRANSPARENT)
    width, height = 520, size

    surface = tk.Canvas(chat, bg=TRANSPARENT, highlightthickness=0)
    # A thick line with round caps forms the input capsule.
    capsule = surface.create_line(0, 0, 0, 0, fill=PANEL, width=58,
                                  capstyle="round")
    content = tk.Frame(surface, bg=PANEL)
    # A Canvas can position and clip an embedded Frame during the slide animation.
    controls = surface.create_window(0, height / 2, anchor="w", window=content)
    header = tk.Frame(content, bg=PANEL, cursor="fleur")
    header.pack(side="right", fill="y")
    close_button = tk.Button(header, text="×", bg=PANEL, fg=TEXT,
                             activebackground=FIELD, activeforeground=TEXT,
                             relief="flat", font=("Segoe UI", 15), cursor="hand2")
    close_button.pack(expand=True)
    make_draggable(header, orb)
    # Dragging the chat's trailing header moves the orb; position_chat follows it.

    composer = tk.Frame(content, bg=PANEL)
    composer.pack(side="left", fill="both", expand=True)
    draft = tk.Entry(composer, bg=FIELD, fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Segoe UI", 12), width=1)
    draft.insert(0, "Type a message…")
    draft.configure(fg=MUTED)
    placeholder_visible = True
    current_theme = THEMES["dark"].copy()
    # Track the placeholder explicitly so theme color changes cannot erase a draft.

    def clear_placeholder(_event):
        """Remove the hint on the first click or keypress."""
        nonlocal placeholder_visible
        if placeholder_visible:
            placeholder_visible = False
            draft.delete(0, "end")
            draft.configure(fg=current_theme["text"])

    draft.bind("<KeyPress>", clear_placeholder)
    draft.bind("<ButtonPress-1>", clear_placeholder)
    draft.pack(side="left", fill="x", expand=True, ipady=8)
    def rounded_surface(width, height, spacing):
        """Draw the curved ends around a native control; Tk buttons are rectangular."""
        shell = tk.Canvas(composer, width=width, height=height, bg=PANEL,
                          borderwidth=0, highlightthickness=0)
        shell.pack(side="right", padx=spacing)
        radius = height / 2
        if width == height:
            shell.create_oval(1, 1, width - 1, height - 1, outline="",
                              fill=FIELD, tags="face")
        else:
            shell.create_line(radius, radius, width - radius, radius,
                              width=height - 2, capstyle="round", fill=FIELD, tags="face")
        return shell

    # A 28-pixel disc frames a slim arrow. A negative Tk font size uses pixels,
    # so the arrow stays proportional to the disc at different font settings.
    send_shell = rounded_surface(28, 28, (5, 7))
    send_button = tk.Button(
        send_shell,
        text="↑",
        bg=PANEL,
        fg=TEXT,
        activebackground=FIELD,
        activeforeground=TEXT,
        cursor="hand2",
        relief="flat",
        font=("Segoe UI Symbol", -16, "normal"),
    )
    send_button.configure(borderwidth=0, highlightthickness=0, padx=0, pady=0)
    send_shell.create_window(14, 14, window=send_button, width=17, height=20)
    send_shell.tag_bind("face", "<ButtonRelease-1>", lambda _event: send_button.invoke())

    mic_shell = rounded_surface(82, 28, (4, 0))
    mic_button = tk.Button(mic_shell, text="Mute mic", relief="flat", borderwidth=0,
                           highlightthickness=0, cursor="hand2", padx=0, pady=0)
    mic_shell.create_window(41, 14, window=mic_button, width=68, height=22)
    mic_shell.tag_bind("face", "<ButtonRelease-1>", lambda _event: mic_button.invoke())

    selected_agent = tk.StringVar(master=orb, value="general")
    agent_label = tk.StringVar(master=orb, value="General  ▾")
    # Keep the API identifier separate from its human-readable button label.
    agent_shell = rounded_surface(110, 32, (6, 0))
    agent_button = tk.Button(
        agent_shell,
        textvariable=agent_label,
        bg=PANEL,
        fg=MUTED,
        activebackground="#252525",
        activeforeground=TEXT,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        font=("Segoe UI", 10),
        padx=8,
        pady=6,
    )
    agent_shell.create_window(55, 16, window=agent_button, width=88, height=22)
    agents = ("general", "personal", "academic", "trading")
    row_height, rows_top, picker_width = 35, 36, 182
    picker_height = rows_top + row_height * len(agents) + 8
    picker = tk.Toplevel(chat)
    picker.withdraw()
    picker.overrideredirect(True)
    picker.attributes("-topmost", True)
    picker.attributes("-transparentcolor", TRANSPARENT)
    picker.attributes("-alpha", 0.91)
    choices = tk.Canvas(picker, bg=TRANSPARENT, highlightthickness=0)
    choices.pack(fill="both", expand=True)
    highlighted = 0

    def draw_choices():
        """Use the composer's palette and leave the rounded corners transparent."""
        choices.delete("all")
        w, h, r = picker_width, picker_height, 15
        c = current_theme
        choices.create_polygon(r,1,w-r,1,w-1,1,w-1,r,w-1,h-r,w-1,h-1,
                               w-r,h-1,r,h-1,1,h-1,1,h-r,1,r,1,1,
                               smooth=True, fill=c["panel"], outline=c["hover"])
        choices.create_text(17, 19, anchor="w", text="Choose agent",
                            fill=c["muted"], font=("Segoe UI", 9))
        for i, agent in enumerate(agents):
            y = rows_top + (i + 0.5) * row_height
            if i == highlighted:
                choices.create_line(23, y, w-23, y, width=30, capstyle="round",
                                    fill=c["hover"])
            choices.create_text(20, y, anchor="w", text=agent.title(),
                                fill=c["text"], font=("Segoe UI", 10))
            if selected_agent.get() == agent:
                choices.create_text(w-23, y, text="✓", fill=c["text"])

    def dismiss_picker():
        """Release menu input and return to the composer."""
        if picker.grab_current() == choices:
            choices.grab_release()
        picker.withdraw()

    def choose_agent(index):
        """Use the highlighted specialist for subsequent messages."""
        selected_agent.set(agents[index])
        agent_label.set(f"{agents[index].title()}  ▾")
        dismiss_picker()
        draft.focus_set()

    def highlight(index):
        nonlocal highlighted
        highlighted = index % len(agents)
        draw_choices()

    def pointer_choice(event):
        """Use screen coordinates so clicks outside the grabbed popup dismiss it."""
        x = event.x_root - choices.winfo_rootx()
        y = event.y_root - choices.winfo_rooty()
        index = (y - rows_top) // row_height
        inside = 7 <= x < picker_width - 7 and 0 <= index < len(agents)
        if event.type == tk.EventType.ButtonPress:
            if inside:
                choose_agent(index)
            else:
                dismiss_picker()
        elif inside and index != highlighted:
            highlight(index)

    def open_picker():
        """Align the popup with the selector, using space above or below it."""
        x = max(0, min(agent_shell.winfo_rootx() + agent_shell.winfo_width() - picker_width,
                       orb.winfo_screenwidth() - picker_width))
        y = agent_shell.winfo_rooty() - picker_height - 5
        if y < 0:
            y = agent_shell.winfo_rooty() + agent_shell.winfo_height() + 5
        picker.geometry(f"{picker_width}x{picker_height}+{x}+{y}")
        highlight(agents.index(selected_agent.get()))
        picker.deiconify()
        picker.lift()
        choices.focus_force()
        choices.grab_set()

    agent_button.configure(command=open_picker)
    agent_shell.tag_bind("face", "<ButtonRelease-1>", lambda _e: agent_button.invoke())
    choices.bind("<Motion>", pointer_choice)
    choices.bind("<ButtonPress-1>", pointer_choice)
    choices.bind("<Up>", lambda _e: highlight(highlighted - 1))
    choices.bind("<Down>", lambda _e: highlight(highlighted + 1))
    choices.bind("<Return>", lambda _e: choose_agent(highlighted))
    choices.bind("<space>", lambda _e: choose_agent(highlighted))
    choices.bind("<Escape>", lambda _e: (dismiss_picker(), agent_button.focus_set()))
    choices.bind("<FocusOut>", lambda _e: dismiss_picker())

    progress = 0.0
    # progress is the visible width fraction; opened is the animation's target.
    opened = False
    animation = None
    response_font = tkfont.Font(family="Segoe UI", size=11)
    response = tk.Text(surface, wrap="word", font=response_font, bg=PANEL,
                       fg=TEXT, relief="flat", borderwidth=0, highlightthickness=0,
                       padx=14, pady=12, state="disabled", cursor="arrow")
    response_box = surface.create_window(10, 0, anchor="nw", window=response,
                                         state="hidden")
    # Replies are read-only and appear above the composer only when needed.
    response_text = ""

    def set_response(text):
        """Set preview content and resize the panel. Call on the Tk UI thread."""
        nonlocal response_text
        response_text = str(text)
        # Temporarily unlock the display to replace its text, then make it read-only.
        response.configure(state="normal")
        response.delete("1.0", "end")
        response.insert("1.0", response_text)
        response.configure(state="disabled")
        position_chat()

    # Expose the display callback for callers running on the Tk UI thread.
    orb.set_response = set_response

    def position_chat(_event=None):
        """Follow the orb, measure the reply, and clip the panel to its slide width."""
        if not progress:
            return
        x, y = orb.winfo_x(), orb.winfo_y()
        screen_width = orb.winfo_screenwidth()
        # Open toward the screen center and limit width to the available space.
        right = x + size / 2 < screen_width / 2
        # An orb on the left opens right, and an orb on the right opens left.
        available = screen_width - (x + size - 2) if right else x + 2
        panel_width = max(1, min(width, available))
        # Estimate wrapped lines using the actual font's measured word widths.
        line_width = max(1, panel_width - 48)
        lines = 0
        for paragraph in response_text.split("\n"):
            used = 0
            lines += 1
            for word in paragraph.split():
                pixels = response_font.measure(word + " ")
                if used and used + pixels > line_width:
                    lines += 1
                    used = 0
                lines += max(0, (pixels - 1) // line_width)
                used += pixels % line_width
        response_height = min(300, max(64, lines * response_font.metrics("linespace") + 24))
        # Cap the reply height; the Text widget can still scroll longer replies.
        response_height = min(response_height, max(40, orb.winfo_screenheight() - height - 12))
        has_response = bool(response_text.strip())
        # Reserve space above the input only while there is a reply or status.
        offset = response_height + 8 if has_response else 0
        total_height = height + offset
        panel_y = max(0, min(y - offset, orb.winfo_screenheight() - total_height))
        visible = max(1, round(panel_width * progress))
        panel_x = x + size - 2 if right else x - visible + 2
        chat.geometry(f"{visible}x{total_height}+{panel_x}+{panel_y}")
        # Clip the full surface to the animated window width for the sliding effect.
        surface.place(x=0 if right else visible - panel_width, y=0,
                      width=panel_width, height=total_height)
        surface.itemconfigure(response_box, width=max(1, panel_width - 20),
                              height=response_height,
                              state="normal" if has_response else "hidden")
        surface.coords(capsule, 29, offset + height / 2,
                       max(30, panel_width - 29), offset + height / 2)
        surface.coords(controls, 25, offset + height / 2)
        surface.itemconfigure(controls, width=max(1, panel_width - 48))

    def animate():
        """Advance the sliding window toward its current open/closed target."""
        # Each scheduled tick moves toward the latest open or closed target.
        nonlocal progress, animation
        progress = min(1.0, progress + 0.065) if opened else max(0.0, progress - 0.065)
        if progress:
            position_chat()
            if chat.state() == "withdrawn":
                chat.deiconify()
                orb.lift()
        else:
            chat.withdraw()

        if 0 < progress < 1:
            animation = orb.after(15, animate)
        else:
            animation = None
            if opened:
                draft.focus_set()

    def toggle_chat():
        """Reverse the target while allowing an in-progress animation to continue."""
        nonlocal opened
        opened = not opened
        # An existing animation will pick up the new target on its next tick.
        if animation is None:
            animate()

    def close_chat():
        """Request a closing animation if the panel is currently opening or open."""
        if opened:
            toggle_chat()

    menu = tk.Menu(orb, tearoff=False)
    menu.add_command(label="Quit PT Orb", command=orb.destroy)

    def show_menu(event):
        """Open the right-click quit menu and release its mouse grab afterward."""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    make_draggable(canvas, orb, toggle_chat)
    canvas.bind("<Button-3>", show_menu)
    close_button.configure(command=close_chat)
    # Follow the orb whenever its window moves or changes size.
    orb.bind("<Configure>", position_chat)
    chat.bind("<Escape>", lambda _event: close_chat())

    # Workers put results here; only the Tk thread reads them and updates widgets.
    replies = queue.Queue()
    transcripts = queue.Queue()
    recent_playback = deque(maxlen=8)
    voice = None
    speech_done = queue.Queue()
    speaking = False

    def play_reply(answer):
        nonlocal voice
        started = None
        try:
            if voice is None:
                model = Path(__file__).resolve().parents[2] / "en_GB-jenny_dioco-medium.onnx"
                voice = PiperVoice.load(str(model))
            started = perf_counter()
            speak(answer, voice)
        except Exception as error:
            print(f"PT voice error: {error}")
        finally:
            speech_done.put((answer, started, perf_counter()))

    listener_errors = queue.Queue()
    listener = None
    muted = False
    mic_generation = 0
    sending = False

    def read_microphone(process, generation):
        # A single pause can produce several timestamped lines in one block.
        parts = []
        with process.stdout as lines:
            for line in lines:
                segment = re.match(r"^\[[\d:.,]+ --> [\d:.,]+\]\s*(.+)", line)
                if segment:
                    parts.append(segment.group(1).strip())
                elif re.fullmatch(r"### Transcription \d+ END", line.strip()):
                    message = " ".join(parts).strip()
                    if has_speech(message):
                        transcripts.put((message, listening_context(), perf_counter(), generation))
                    parts.clear()
        exit_code = process.wait()
        if listener is process:
            listener_errors.put(f"Microphone listener stopped (exit {exit_code}).")

    def stop_microphone():
        nonlocal listener
        process = listener
        listener = None
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait()

    def start_microphone():
        nonlocal listener
        if muted or sending or speaking or (listener is not None and listener.poll() is None):
            return
        folder = Path(__file__).resolve().parents[2] / "Whisper"
        try:
            listener = subprocess.Popen(
                [str(folder / "whisper-stream.exe"), "-m", str(folder / "ggml-base.bin"),
                 "--step", "0", "-l", "en"],
                stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except OSError as error:
            listener_errors.put(f"Could not start microphone listener: {error}")
            return
        threading.Thread(target=read_microphone, args=(listener, mic_generation), daemon=True).start()

    def toggle_microphone():
        nonlocal muted, mic_generation
        muted = not muted
        mic_button.configure(text="Unmute mic" if muted else "Mute mic")
        if muted:
            mic_generation += 1
            stop_microphone()
        else:
            start_microphone()

    mic_button.configure(command=toggle_microphone)

    def request_reply(message, agent, context, was_listening):
        """Send plain values to the backend and queue a reply or readable error."""
        # Runs in a worker thread. Communicate with the UI through the queue.
        try:
            result = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"message": message, "agent": agent, "desktop_context": context,
                      "listening": was_listening},
                timeout=300,
            )
            result.raise_for_status()

            # server.py returns a JSON object containing the completed reply.
            payload = result.json()
            answer = payload["reply"]
            if not isinstance(answer, str):
                raise ValueError("The server returned an invalid reply.")

            replies.put((answer, True))
        except (requests.RequestException, ValueError, KeyError) as error:
            # Route failures through the same display path as successful replies.
            replies.put((f"Could not get a reply: {error}", False))

    def send_message(_event=None):
        """Validate the draft, capture the agent, and launch one HTTP request."""

        # Ignore repeat sends and the placeholder while a request is pending.
        if sending or speaking or placeholder_visible:
            return

        # Read Tk widgets here, before handing plain text to the worker.
        message = draft.get().strip()
        if not message:
            return

        draft.delete(0, "end")
        dispatch(message, "unknown")

    def dispatch(message, context):
        nonlocal sending
        sending = True
        was_listening = listener is not None and listener.poll() is None
        stop_microphone()
        send_button.configure(state="disabled")
        agent_button.configure(state="disabled")
        # Freeze selection until completion so the visible agent matches this reply.
        agent = selected_agent.get()
        set_response("Thinking…")

        # The network call runs separately so it cannot block Tk's event loop.
        # A daemon worker does not keep the orb process alive after closing it.
        threading.Thread(
            target=request_reply,
            args=(message, agent, context, was_listening),
            daemon=True,
        ).start()

    def check_replies():
        """Poll the thread-safe queue every 50 ms without blocking Tk."""
        # This callback runs on the UI thread and never waits for a result.
        nonlocal sending, speaking
        try:
            error = listener_errors.get_nowait()
        except queue.Empty:
            pass
        else:
            set_response(error)
            if not opened:
                toggle_chat()
        try:
            answer, success = replies.get_nowait()
        except queue.Empty:
            pass
        else:
            set_response(answer)
            sending = False
            if answer and not opened:
                toggle_chat()
            if success and answer.strip():
                speaking = True
                worker = threading.Thread(target=play_reply, args=(answer,), daemon=True)
                orb.after_idle(lambda: orb.after(0, worker.start))
            else:
                start_microphone()

        try:
            spoken, started, ended = speech_done.get_nowait()
        except queue.Empty:
            pass
        else:
            if started is not None:
                recent_playback.append((spoken, started, ended))
            speaking = False
            start_microphone()

        if not sending and not speaking:
            send_button.configure(state="normal")
            agent_button.configure(state="normal")
            try:
                text, context, heard_at, generation = transcripts.get_nowait()
            except queue.Empty:
                pass
            else:
                if not muted and generation == mic_generation and not is_playback_echo(text, heard_at, recent_playback):
                    dispatch(text, context)

        # Keep polling after both empty checks and completed requests.
        orb.after(50, check_replies)

    # Both input methods share validation, loading state, and request handling.
    send_button.configure(command=send_message)
    draft.bind("<Return>", send_message)
    check_replies()

    def apply_theme(colors):
        """Apply the same palette to input, replies, buttons, and both menus."""
        current_theme.update(colors)
        panel, text = colors["panel"], colors["text"]
        for widget in (content, header, composer):
            widget.configure(bg=panel)
        surface.itemconfigure(capsule, fill=panel)
        draft.configure(bg=panel, fg=colors["muted"] if placeholder_visible else text,
                        insertbackground=text, selectbackground=colors["hover"],
                        selectforeground=text)
        response.configure(bg=panel, fg=text, selectbackground=colors["hover"],
                           selectforeground=text)
        close_button.configure(bg=panel, fg=text, activebackground=colors["hover"],
                               activeforeground=text, disabledforeground=colors["muted"])
        # Both controls use the same surface and foreground in each palette.
        face = colors["hover"]
        for shell, widget in ((agent_shell, agent_button), (send_shell, send_button),
                              (mic_shell, mic_button)):
            shell.configure(bg=panel)
            shell.itemconfigure("face", fill=face)
            widget.configure(bg=face, fg=text, activebackground=face,
                             activeforeground=text, disabledforeground=colors["muted"])
        menu.configure(bg=panel, fg=text, activebackground=colors["hover"],
                       activeforeground=text)
        if picker.winfo_ismapped():
            draw_choices()

    theme_name = "dark"
    pending_theme = None
    # theme_name is committed; pending_theme tracks the previous screen reading.

    def transition_theme(target, step=1, start=None):
        """Blend RGB channels over ten frames, taking approximately 200 ms."""
        start = current_theme.copy() if start is None else start
        fraction = step / 10
        colors = {}
        for key, end in THEMES[target].items():
            # Interpolate each pair of hexadecimal red, green, and blue digits.
            channels = [
                round(int(start[key][i:i + 2], 16) * (1 - fraction)
                      + int(end[i:i + 2], 16) * fraction)
                for i in (1, 3, 5)
            ]
            colors[key] = "#" + "".join(f"{channel:02x}" for channel in channels)
        apply_theme(colors)
        if step < 10:
            orb.after(20, transition_theme, target, step + 1, start)

    def check_background():
        """Sample nearby colors and switch palettes after two consistent readings."""
        nonlocal theme_name, pending_theme
        brightness = background_brightness((orb, chat))
        target = theme_name
        if brightness is not None:
            # The gap between thresholds keeps ambiguous gray backgrounds stable.
            if brightness > 0.49:
                target = "light"
            elif brightness < 0.36:
                target = "dark"
        # Require two consistent samples and a neutral band to avoid flickering.
        if target != theme_name and target == pending_theme:
            theme_name = target
            orb.status_icon.set_background(target)
            transition_theme(target)
        pending_theme = target
        orb.after(900, check_background)

    apply_theme(current_theme)
    # Start theme detection after Tk has had time to position its windows.
    orb.after(300, check_background)
    # Tk now handles input, animation timers, and queued replies until Quit.
    orb.after_idle(start_microphone)
    try:
        orb.mainloop()
    finally:
        stop_microphone()


if __name__ == "__main__":
    # Launch only when run as a script, so importing does not open desktop windows.
    main()
