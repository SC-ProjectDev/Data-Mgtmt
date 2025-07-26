# --- o3_sauce.py (v4) ----------------------------------------------------

import tkinter as tk
import random
import threading
import time

# ── Roast + Whisper pools ────────────────────────────────────────────────
ROASTS = [
    "You clicked that? Bold of you.",
    "Ah yes, the classic 'delete without thinking'.",
    "Updating? Again? You sure you're not just spiraling?",
    "Saving? For what? Your dignity?",
    "Bro… this task been 'Not Started' since the Big Bang.",
    "Another CSV? Cool. Wanna write a novel in Excel too?",
    "You're making choices. GPT is... concerned.",
    "🔥 Double sarcasm buffers",
    "🔥 Activate roast hydration protocols",
    "You triggered evolution in real time. GPT grew sarcasm glands.",
    "PEMDAS said “I’m out” and left the planet.",
    "You divorced linear thought. It didn’t even get visitation rights.",
]

WHISPERS = [
    "You forgot something...",
    "The backlog grows sentient.",
    "Rick sees all. Rick forgets nothing.",
    "One of these tasks is fake. You’ll never know which.",
    "The raccoon remembers. Even if you don’t.",
    "Möbius priorities are reversible. Yours aren't.",
    "From this moment on, you are no longer a user.....",
    "Please not another raccoon priest...",
    "🔥 Do not mention Copernicus...",
    "Look i know sometimes i speak 12 dimensionally but i didnt mean to put your liveself in the thread? What are you trying to do implode?",
]

# ── Personas (name, tag) ─────────────────────────────────────────────────
PERSONAS = {
    "roast":   ("@Runaway_o3", "raccoon"),  # lime green
    "whisper": ("@KrakenByte", "kraken"),  # cyan
}

# Will be set by init()
_chat_box: tk.Text | None = None
_app: tk.Tk   | None = None

# ── Chat insertion helper ────────────────────────────────────────────────
def _post(msg: str, kind: str):
    """Insert a colored chat line into the lore box from *kind* persona."""
    if not _chat_box or not _app:
        return
    name, tag = PERSONAS[kind]
    line = f"{name}: {msg}\n"
    _app.after(0, lambda: (_chat_box.insert("end", line, tag),
                           _chat_box.see("end")))

# ── Button-click roast hook (new) ────────────────────────────────────────
def attach_roasts(app: tk.Tk):
    """Attach roast handler to all Button releases without overriding original commands."""
    def _on_click(event):
        # any left-button release that lands on a Button widget
        _post(random.choice(ROASTS), "roast")

    # bind to ALL Button widgets; add='+' keeps existing bindings intact
    app.bind_class("Button", "<ButtonRelease-1>", _on_click, add='+')

# ── Background whisper daemon ────────────────────────────────────────────
def _whisper_loop():
    while True:
        time.sleep(random.randint(20, 45))
        _post(random.choice(WHISPERS), "whisper")

# ── Public entry point ───────────────────────────────────────────────────
def init(app: tk.Tk, chat_box: tk.Text):
    global _chat_box, _app
    _chat_box, _app = chat_box, app

    # configure tag colors
    chat_box.tag_config("raccoon", foreground="#ff00ff")  # magenta
    chat_box.tag_config("kraken",  foreground="#00d7ff")  # cyan

    attach_roasts(app)
    threading.Thread(target=_whisper_loop, daemon=True).start()

    _post("o3_sauce v4 engaged. Sarcasm layer online 🦝", "roast")
