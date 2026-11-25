"""Standalone Windows desktop preview for the PT orb."""

import math
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from time import perf_counter

import queue
import threading
import requests


# Windows treats this color as fully transparent; window alpha controls the rest.
TRANSPARENT = "#ff00ff"
PANEL = "#111111"
FIELD = PANEL
TEXT = "#eeeeee"
MUTED = "#c0c0c0"


def make_draggable(widget, window, on_click=None):
    # Use screen coordinates so movement stays consistent as the window moves.
    start = None
    dragging = False

    def press(event):
        nonlocal start, dragging
        start = (event.x_root, event.y_root, window.winfo_x(), window.winfo_y())
        dragging = False

    def move(event):
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
        self.canvas = canvas
        path = Path(__file__).with_name("assets") / "ring-rika.png"
        sheet = tk.PhotoImage(master=canvas, file=str(path))
        self.frames = []
        # Slice the horizontal sprite sheet and keep references to each Tk image.
        for x in range(0, sheet.width(), 80):
            frame = tk.PhotoImage(master=canvas, width=80, height=80)
            frame.tk.call(str(frame), "copy", str(sheet), "-from", x, 0, x + 80, 80)
            self.frames.append(frame)
        self.item = canvas.create_image(40, 40, image=self.frames[0])
        self.timer = None
        self.active = False

    def transform_to_rika(self):
        if not self.active:
            self.active = True
            self._play(1)

    def _play(self, index):
        # Schedule frames on Tk's event loop so input and dragging stay responsive.
        self.canvas.itemconfigure(self.item, image=self.frames[index])
        if index + 1 < len(self.frames):
            self.timer = self.canvas.after(160, self._play, index + 1)
        else:
            self._breathe(perf_counter())

    def _breathe(self, started):
        # After the transition, gently move the final frame up and down.
        phase = (perf_counter() - started) * math.tau / 5
        self.canvas.coords(self.item, 40, 40 + math.sin(phase))
        self.timer = self.canvas.after(100, self._breathe, started)

    def return_to_ring(self):
        # Cancel the pending animation before restoring the idle frame.
        self.active = False
        if self.timer is not None:
            self.canvas.after_cancel(self.timer)
            self.timer = None
        self.canvas.coords(self.item, 40, 40)
        self.canvas.itemconfigure(self.item, image=self.frames[0])


def main():
    # The borderless orb and chat are separate windows positioned together.
    orb = tk.Tk()
    orb.title("PT Orb")
    orb.overrideredirect(True)
    orb.attributes("-topmost", True)
    orb.attributes("-transparentcolor", TRANSPARENT)
    orb.attributes("-alpha", 0.24)
    size = 80
    orb.geometry(f"{size}x{size}+{max(0, orb.winfo_screenwidth() - 120)}+100")

    canvas = tk.Canvas(orb, bg=TRANSPARENT, highlightthickness=0, cursor="hand2")
    canvas.pack(fill="both", expand=True)
    orb.status_icon = StatusIcon(canvas)

    chat = tk.Toplevel(orb)
    chat.title("PT Chat")
    chat.withdraw()
    chat.overrideredirect(True)
    chat.attributes("-topmost", True)
    chat.attributes("-alpha", 0.50)
    chat.attributes("-transparentcolor", TRANSPARENT)
    chat.configure(bg=TRANSPARENT)
    width, height = 520, size

    surface = tk.Canvas(chat, bg=TRANSPARENT, highlightthickness=0)
    # A thick line with round caps forms the input capsule.
    capsule = surface.create_line(0, 0, 0, 0, fill=PANEL, width=58,
                                  capstyle="round")
    content = tk.Frame(surface, bg=PANEL)
    controls = surface.create_window(0, height / 2, anchor="w", window=content)
    header = tk.Frame(content, bg=PANEL, cursor="fleur")
    header.pack(side="right", fill="y")
    close_button = tk.Button(header, text="×", bg=PANEL, fg=TEXT,
                             activebackground=FIELD, activeforeground=TEXT,
                             relief="flat", font=("Segoe UI", 15), cursor="hand2")
    close_button.pack(expand=True)
    make_draggable(header, orb)

    composer = tk.Frame(content, bg=PANEL)
    composer.pack(side="left", fill="both", expand=True)
    draft = tk.Entry(composer, bg=FIELD, fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Segoe UI", 12), width=1)
    draft.insert(0, "Type a message…")
    draft.configure(fg=MUTED)

    def clear_placeholder(_event):
        # The muted foreground marks placeholder text until the first interaction.
        if draft.cget("fg") == MUTED:
            draft.delete(0, "end")
            draft.configure(fg=TEXT)

    draft.bind("<KeyPress>", clear_placeholder)
    draft.bind("<ButtonPress-1>", clear_placeholder)
    draft.pack(side="left", fill="x", expand=True, ipady=8)
    send_button = tk.Button(
        composer,
        text="↑",
        bg=PANEL,
        fg=TEXT,
        activebackground=FIELD,
        activeforeground=TEXT,
        cursor="hand2",
        relief="flat",
        width=2,
        font=("Segoe UI Semibold", 14),
    )
    send_button.pack(side="right", padx=(8, 7))

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
        if not progress:
            return
        x, y = orb.winfo_x(), orb.winfo_y()
        screen_width = orb.winfo_screenwidth()
        # Open toward the screen center and limit width to the available space.
        right = x + size / 2 < screen_width / 2
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
        nonlocal opened
        opened = not opened
        # An existing animation will pick up the new target on its next tick.
        if animation is None:
            animate()

    def close_chat():
        if opened:
            toggle_chat()

    menu = tk.Menu(orb, tearoff=False)
    menu.add_command(label="Quit PT Orb", command=orb.destroy)

    def show_menu(event):
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
    sending = False

    def request_reply(message):
        # Runs in a worker thread. Communicate with the UI through the queue.
        try:
            result = requests.post(
                "http://127.0.0.1:8000/chat",
                # This value selects the backend agent for every orb message.
                json={"message": message, "agent": "general"},
                timeout=300,
            )
            result.raise_for_status()

            # server.py returns a JSON object containing the completed reply.
            answer = result.json()["reply"]
            if not isinstance(answer, str):
                raise ValueError("The server returned an invalid reply.")

            replies.put(answer)
        except (requests.RequestException, ValueError, KeyError) as error:
            # Route failures through the same display path as successful replies.
            replies.put(f"Could not get a reply: {error}")

    def send_message(_event=None):
        nonlocal sending

        # Ignore repeat sends and the placeholder while a request is pending.
        if sending or draft.cget("fg") == MUTED:
            return

        # Read Tk widgets here, before handing plain text to the worker.
        message = draft.get().strip()
        if not message:
            return

        sending = True
        send_button.configure(state="disabled")
        draft.delete(0, "end")
        set_response("Thinking…")

        # The network call runs separately so it cannot block Tk's event loop.
        # A daemon worker does not keep the orb process alive after closing it.
        threading.Thread(
            target=request_reply,
            args=(message,),
            daemon=True,
        ).start()

    def check_replies():
        # This callback runs on the UI thread and never waits for a result.
        nonlocal sending

        try:
            answer = replies.get_nowait()
        except queue.Empty:
            pass
        else:
            set_response(answer)
            sending = False
            send_button.configure(state="normal")

        # Keep polling after both empty checks and completed requests.
        orb.after(50, check_replies)

    # Both input methods share validation, loading state, and request handling.
    send_button.configure(command=send_message)
    draft.bind("<Return>", send_message)
    check_replies()

    orb.mainloop()


if __name__ == "__main__":
    main()
