import tkinter as tk
from tkinter import ttk, messagebox
from db import (
    init_db, add_activity, get_activities,
    add_time, get_today_times, hide_activity,
    show_activity
)
from timer import Timer


init_db()

timers = {}
timer_labels = {}
active_timer_id = None
floating_window = None
floating_label = None
floating_title = None
drag_x = 0
drag_y = 0

# ---------------- UTILIDADES ---------------- #

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# ---------------- LOGICA ---------------- #


def add_new_activity():
    name = entry.get()
    if name:
        add_activity(name)
        entry.delete(0, tk.END)
        load_activities()

def start_timer(act_id, name):
    global active_timer_id

    if active_timer_id is not None and active_timer_id != act_id:
        stop_timer(active_timer_id)

    timers[act_id].start()
    active_timer_id = act_id
    open_floating_timer(name)

def stop_timer(act_id):
    global active_timer_id

    timer = timers[act_id]
    timer.stop()
    add_time(act_id, timer.elapsed)
    timer.reset()

    if active_timer_id == act_id:
        active_timer_id = None
        close_floating_timer()

    refresh_table()

def remove_activity(act_id):
    if active_timer_id == act_id:
        stop_timer(act_id)

    hide_activity(act_id)

    timers.pop(act_id, None)
    timer_labels.pop(act_id, None)

    load_activities()
    refresh_table()

def start_move(event):
    global drag_x, drag_y
    drag_x = event.x
    drag_y = event.y

def do_move(event):
    x = event.x_root - drag_x
    y = event.y_root - drag_y
    floating_window.geometry(f"+{x}+{y}")

# ---------------- VENTANA FLOTANTE ---------------- #

def open_floating_timer(activity_name):
    global floating_window, floating_label, floating_title

    close_floating_timer()

    floating_window = tk.Toplevel(root)
    floating_window.overrideredirect(True)
    floating_window.attributes("-topmost", True)
    floating_window.configure(bg="#222")

    floating_window.geometry("130x50+5+5")

    floating_title = tk.Label(
        floating_window,
        text=activity_name,
        fg="white",
        bg="#222",
        font=("Segoe UI", 10)
    )
    floating_title.pack(pady=(8, 0))

    floating_label = tk.Label(
        floating_window,
        text="00:00:00",
        fg="white",
        bg="#222",
        font=("Consolas", 16, "bold")
    )
    floating_label.pack()

    # 🔑 DRAG
    floating_window.bind("<Button-1>", start_move)
    floating_window.bind("<B1-Motion>", do_move)
    floating_title.bind("<Button-1>", start_move)
    floating_title.bind("<B1-Motion>", do_move)
    floating_label.bind("<Button-1>", start_move)
    floating_label.bind("<B1-Motion>", do_move)

def close_floating_timer():
    global floating_window
    if floating_window:
        floating_window.destroy()
        floating_window = None

# ---------------- UI ---------------- #

def load_activities():
    timer_labels.clear()   # 🔑 CLAVE
    for widget in frame_activities.winfo_children():
        widget.destroy()

    activities = get_activities()

    for row_index, (act_id, name) in enumerate(activities):
        timers.setdefault(act_id, Timer())

        row = tk.Frame(frame_activities)
        row.grid(row=row_index, column=0, pady=4, sticky="ew")
        row.columnconfigure(1, weight=1)

        lbl_name = tk.Label(row, text=name, width=18, anchor="w")
        lbl_name.grid(row=0, column=0, padx=5)

        lbl_time = tk.Label(
            row,
            text="00:00:00",
            width=10,
            font=("Consolas", 12)
        )
        lbl_time.grid(row=0, column=1)

        timer_labels[act_id] = lbl_time

        tk.Button(
            row, text="Start", width=7,
            command=lambda i=act_id, n=name: start_timer(i, n)
        ).grid(row=0, column=2, padx=2)

        tk.Button(
            row, text="Stop", width=7,
            command=lambda i=act_id: stop_timer(i)
        ).grid(row=0, column=3, padx=2)

        tk.Button(
            row, text="Eliminar", width=8,
            command=lambda i=act_id: remove_activity(i)
        ).grid(row=0, column=4, padx=2)

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)

    for name, seconds in get_today_times():
        tree.insert("", tk.END, values=(name, format_time(seconds)))

def update_timers():
    for act_id, timer in timers.items():
        timer_labels[act_id].config(
            text=format_time(timer.get_elapsed())
        )

    if active_timer_id and floating_label:
        floating_label.config(
            text=format_time(timers[active_timer_id].get_elapsed())
        )

    root.after(500, update_timers)


def open_activity_manager():
    manager = tk.Toplevel(root)
    manager.title("Gestionar actividades")
    manager.geometry("400x300")

    frame = tk.Frame(manager)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    activities = get_activities(active_only=False)

    for act_id, name, active in activities:
        row = tk.Frame(frame)
        row.pack(fill="x", pady=2)

        tk.Label(row, text=name, anchor="w").pack(side=tk.LEFT, fill="x", expand=True)

        if active:
            tk.Button(
                row, text="Ocultar",
                command=lambda i=act_id: (
                    hide_activity(i),
                    manager.destroy(),
                    load_activities(),
                    refresh_table()
                )
            ).pack(side=tk.RIGHT)
        else:
            tk.Button(
                row, text="Mostrar",
                command=lambda i=act_id: (
                    show_activity(i),
                    manager.destroy(),
                    load_activities(),
                    refresh_table()
                )
            ).pack(side=tk.RIGHT)

# ---------------- MAIN ---------------- #

root = tk.Tk()
root.title("Activity Time Tracker")
root.geometry("600x520")

root.columnconfigure(0, weight=1)

top = tk.Frame(root)
top.grid(row=0, column=0, pady=10)

entry = tk.Entry(top, width=30)
entry.grid(row=0, column=0, padx=5)

tk.Button(top, text="Gestionar actividades", command=open_activity_manager)\
    .grid(row=1, column=0, columnspan=2, pady=5)

tk.Button(top, text="Agregar actividad", command=add_new_activity)\
    .grid(row=0, column=1)

frame_activities_container = tk.Frame(root)
frame_activities_container.grid(row=1, column=0, sticky="nsew")
frame_activities_container.columnconfigure(0, weight=1)

frame_activities = tk.Frame(frame_activities_container)
frame_activities.grid(row=0, column=0, padx=20)

tree = ttk.Treeview(
    root,
    columns=("Actividad", "Tiempo"),
    show="headings",
    height=6
)
tree.heading("Actividad", text="Actividad")
tree.heading("Tiempo", text="Tiempo hoy")
tree.grid(row=2, column=0, pady=15, padx=20, sticky="ew")

load_activities()
refresh_table()
update_timers()

root.mainloop()
