import customtkinter as ctk
import pytesseract
import pyperclip
import pyautogui
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
import os

# Set the path for tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to select screen region
def select_area():
    root = tk.Tk()
    root.withdraw()  # Hide main window

    selection = {"x": 0, "y": 0, "w": 0, "h": 0}

    selection_window = tk.Toplevel(root)
    selection_window.attributes("-fullscreen", True)
    selection_window.attributes("-alpha", 0.3)
    selection_window.configure(bg="black")

    overlay = tk.Canvas(selection_window, width=selection_window.winfo_screenwidth(), height=selection_window.winfo_screenheight())
    overlay.pack(fill="both", expand=True)

    # This function will be called to show the selection rectangle
    def update_overlay(event):
        # Only update when dragging, not before
        if selection["x"] != 0 and selection["y"] != 0:
            overlay.delete("all")  # Clear previous rectangle
            selection["w"], selection["h"] = event.x_root - selection["x"], event.y_root - selection["y"]
            overlay.create_rectangle(selection["x"], selection["y"], event.x_root, event.y_root, outline="red", width=2)

    # This function is called on mouse press
    def on_press(event):
        selection["x"], selection["y"] = event.x_root, event.y_root

    # This function is called on mouse release
    def on_release(event):
        selection["w"], selection["h"] = event.x_root - selection["x"], event.y_root - selection["y"]
        overlay.delete("all")  # Clear overlay after selection
        selection_window.destroy()

    # Bind the mouse press, release, and motion events
    selection_window.bind("<ButtonPress-1>", on_press)
    selection_window.bind("<ButtonRelease-1>", on_release)
    selection_window.bind("<Motion>", update_overlay)

    root.wait_window(selection_window)  # Wait for the selection window to close
    root.destroy()  # Close the root window properly
    return selection

# Function to capture selected area and extract text
def capture_and_extract_text():
    selection = select_area()

    if selection["w"] > 0 and selection["h"] > 0:
        screenshot = pyautogui.screenshot(region=(selection["x"], selection["y"], selection["w"], selection["h"]))
        screenshot = np.array(screenshot)  # Convert to NumPy array
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)  # Convert to grayscale

        try:
            extracted_text = pytesseract.image_to_string(screenshot).strip()

            # Clear the terminal before inserting new text
            terminal_textbox.configure(state="normal")
            terminal_textbox.delete("1.0", tk.END)  # Clear previous text

            if extracted_text:
                pyperclip.copy(extracted_text)
                terminal_textbox.insert(tk.END, extracted_text)  # Insert new text
                
                app.after(100, lambda: result_label.configure(text="Text copied to clipboard!", text_color="green"))
            else:
                app.after(100, lambda: result_label.configure(text="No text detected.", text_color="orange"))

            terminal_textbox.configure(state="disabled")  # Disable editing
        except Exception as e:
            app.after(100, lambda: result_label.configure(text=f"OCR Error: {e}", text_color="red"))
    else:
        app.after(100, lambda: result_label.configure(text="Invalid selection. Try again.", text_color="red"))

# Function to handle window close event
def on_closing():
    app.quit()
    app.destroy()

# GUI Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Dawson's OCR Screen Text Capture")
app.geometry("500x400")

# Set the window icon from the file path
icon_path = r"\\dawson-server\home\Drive\Documents\Python\OCR image to text\mouse_selector.ico"
app.iconbitmap(icon_path)  # Set the window icon

title_label = ctk.CTkLabel(app, text="Screen Text Capture", font=("Arial", 20))
title_label.pack(pady=10)

capture_button = ctk.CTkButton(app, text="Select Screen Area", command=capture_and_extract_text)
capture_button.pack(pady=10)

result_label = ctk.CTkLabel(app, text="", font=("Arial", 14))
result_label.pack(pady=5)

# Terminal-style output box
terminal_frame = ctk.CTkFrame(app)
terminal_frame.pack(fill="both", expand=True, padx=10, pady=10)

terminal_label = ctk.CTkLabel(terminal_frame, text="Extracted Text:", font=("Arial", 14))
terminal_label.pack(anchor="w", padx=5, pady=2)

terminal_textbox = ctk.CTkTextbox(terminal_frame, height=150, wrap="word", state="disabled", font=("Courier", 12))
terminal_textbox.pack(fill="both", expand=True, padx=5, pady=5)

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
