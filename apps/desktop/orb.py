"""Standalone Windows desktop preview for the PT orb."""

import math
import random
import tkinter as tk
from time import perf_counter


TRANSPARENT = "#ff00ff"
PANEL = "#071825"
FIELD = PANEL
TEXT = "#d4faff"
MUTED = "#8bc4d3"
CYAN = "#42dfff"


def make_draggable(widget, window, on_click=None):
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


def animate_core(canvas):
    """Draw a layered blue energy core using reusable canvas items."""
    rng = random.Random(17)
    started = perf_counter()
    rings = []
    for radius, stretch, tilt, phase, color in (
        (34, 0.91, 0.15, 0.8, "#346487"),
        (29, 0.52, -0.65, 0.4, "#477c9f"),
        (14, 0.92, -0.2, 0.0, "#5b9dbb"),
    ):
        pieces = []
        for index in range(4):
            start = index * math.tau / 4
            span = rng.uniform(0.72, 1.18)
            item = canvas.create_line(0, 0, 0, 0, fill=color,
                                      width=2 if radius <= 14 else 1)
            pieces.append((item, start, span))
        rings.append((radius, stretch, tilt, phase, pieces))

    particles = [
        (canvas.create_oval(0, 0, 0, 0, fill=rng.choice((
            "#3679af", "#50b7ed", "#8ae7ff", "#c3f5ff")), outline=""),
         rng.uniform(8, 37), rng.uniform(0, math.tau),
         rng.uniform(0.6, 1.2))
        for _ in range(7)
    ]
    glow = canvas.create_oval(0, 0, 0, 0, outline="#55c6ff", width=2)
    core = canvas.create_oval(37, 37, 43, 43, fill="#d9faff", outline="")

    def point(radius, stretch, tilt, angle):
        x, y = radius * math.cos(angle), radius * stretch * math.sin(angle)
        return (40 + x * math.cos(tilt) - y * math.sin(tilt),
                40 + x * math.sin(tilt) + y * math.cos(tilt))

    def draw():
        t = perf_counter() - started
        beat = math.tau * t / 2.8
        for radius, stretch, tilt, phase, pieces in rings:
            pulsing_radius = radius * (1 + 0.075 * math.sin(beat - phase))
            for item, start, span in pieces:
                coords = []
                for step in range(9):
                    angle = start + span * step / 8
                    coords.extend(point(pulsing_radius, stretch, tilt, angle))
                canvas.coords(item, *coords)
        for item, radius, phase, size in particles:
            x, y = point(radius * (1 + 0.05 * math.sin(beat - 0.8)), 0.82, 0, phase)
            pulse = size * (0.78 + 0.22 * math.sin(beat - 0.8))
            canvas.coords(item, x - pulse, y - pulse, x + pulse, y + pulse)
        halo = 6 + 1.5 * math.sin(beat)
        canvas.coords(glow, 40 - halo, 40 - halo, 40 + halo, 40 + halo)
        center = 3 + 0.6 * math.sin(beat)
        canvas.coords(core, 40 - center, 40 - center, 40 + center, 40 + center)
        canvas.tag_raise(core)
        canvas.after(33, draw)

    draw()


def main():
    orb = tk.Tk()
    orb.title("PT Orb")
    orb.overrideredirect(True)
    orb.attributes("-topmost", True)
    orb.attributes("-transparentcolor", TRANSPARENT)
    orb.attributes("-alpha", 0.53)
    size = 80
    orb.geometry(f"{size}x{size}+{max(0, orb.winfo_screenwidth() - 120)}+100")

    canvas = tk.Canvas(orb, bg=TRANSPARENT, highlightthickness=0, cursor="hand2")
    canvas.pack(fill="both", expand=True)
    canvas.create_oval(2, 2, 78, 78, fill="#061220", outline="#173753")
    animate_core(canvas)

    chat = tk.Toplevel(orb)
    chat.title("PT Chat")
    chat.withdraw()
    chat.overrideredirect(True)
    chat.attributes("-topmost", True)
    chat.attributes("-alpha", 0.60)
    chat.attributes("-transparentcolor", TRANSPARENT)
    chat.configure(bg=TRANSPARENT)
    width, height = 520, size

    surface = tk.Canvas(chat, bg=TRANSPARENT, highlightthickness=0)
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
        if draft.cget("fg") == MUTED:
            draft.delete(0, "end")
            draft.configure(fg=TEXT)

    draft.bind("<KeyPress>", clear_placeholder)
    draft.bind("<ButtonPress-1>", clear_placeholder)
    draft.pack(side="left", fill="x", expand=True, ipady=8)
    tk.Button(composer, text="↑", state="disabled", bg=PANEL,
              disabledforeground=MUTED, relief="flat", width=2,
              font=("Segoe UI Semibold", 14)).pack(side="right", padx=(8, 7))

    progress = 0.0
    opened = False
    animation = None

    def position_chat(_event=None):
        if not progress:
            return
        x, y = orb.winfo_x(), orb.winfo_y()
        screen_width = orb.winfo_screenwidth()
        right = x + size / 2 < screen_width / 2
        available = screen_width - (x + size - 2) if right else x + 2
        panel_width = max(1, min(width, available))
        visible = max(1, round(panel_width * progress))
        panel_x = x + size - 2 if right else x - visible + 2
        chat.geometry(f"{visible}x{height}+{panel_x}+{y}")
        surface.place(x=0 if right else visible - panel_width, y=0,
                      width=panel_width, height=height)
        surface.coords(capsule, 29, height / 2, max(30, panel_width - 29), height / 2)
        surface.coords(controls, 25, height / 2)
        surface.itemconfigure(controls, width=max(1, panel_width - 48))

    def animate():
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
    orb.bind("<Configure>", position_chat)
    chat.bind("<Escape>", lambda _event: close_chat())
    orb.mainloop()


if __name__ == "__main__":
    main()
