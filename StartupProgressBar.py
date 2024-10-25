import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
PROGRESS_BAR_LENGTH = 1600
PROGRESS_BAR_X = 160
PROGRESS_BAR_Y = 900
PROGRESS_LABEL_X = 900
PROGRESS_LABEL_Y = 950
BACKGROUND_IMAGE_PATH = "/home/item/Ficep_sept24/Ficep_Logo.png"
PROGRESS_DURATION = 52  # in seconds
SLEEP_INTERVAL = 1  # in seconds

def create_main_window():
    root = tk.Tk()
    root.attributes('-fullscreen', True) 
    root.config(cursor="none")  
    return root

def load_background_image():
    bg_image = Image.open(BACKGROUND_IMAGE_PATH)
    bg_image = bg_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.LANCZOS)
    return ImageTk.PhotoImage(bg_image)

def add_background_label(root, bg_photo):
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def add_progress_bar(root):
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=PROGRESS_BAR_LENGTH, mode='determinate')
    progress_bar.place(x=PROGRESS_BAR_X, y=PROGRESS_BAR_Y)
    return progress_bar

def add_progress_label(root):
    progress_label = tk.Label(root, text="0%", font=("Arial", 24), bg="white")
    progress_label.place(x=PROGRESS_LABEL_X, y=PROGRESS_LABEL_Y)
    return progress_label

def update_progress_bar(progress_bar, progress_label):
    progress = 0
    step = 100 / PROGRESS_DURATION

    def update():
        nonlocal progress
        if progress <= 100:
            progress_bar['value'] = progress
            progress_label.config(text=f"{int(progress)}%")
            progress += step
            root.after(int(SLEEP_INTERVAL * 1000), update)
        else:
            root.destroy()

    update()  # Start the update loop

def main():
    global root
    root = create_main_window()

    bg_photo = load_background_image()
    add_background_label(root, bg_photo)

    progress_bar = add_progress_bar(root)
    progress_label = add_progress_label(root)

    # Use threading to prevent freezing on startup
    threading.Thread(target=lambda: update_progress_bar(progress_bar, progress_label)).start()

    root.mainloop()

if __name__ == "__main__":
    main()
