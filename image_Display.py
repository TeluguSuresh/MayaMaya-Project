import time
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.messagebox

def display_images(image_paths):
    root = tk.Tk()
    time.sleep(3)

    for i in image_paths:
        # Load the JPEG image using PIL
        img = Image.open(i)

        # Convert the JPEG image to a PhotoImage object
        image = ImageTk.PhotoImage(img)

        # Display the image in a label widget
        root.geometry("600x800") 

        label = tk.Label(root, image=image)
        label.pack()

        # Show a message box to prompt the user to click "OK" to view the next image
        result = tkinter.messagebox.askokcancel("Image Viewer", "Click OK to view the next image")
        if not result:
            continue
        
        else:
            label.destroy()

    root.mainloop()

image_paths = [
    "D:\\Dhenusya\\Images\\9885977948.JPEG",
    "D:\\Dhenusya\\Images\\630428993.JPEG",
    "D:\\Dhenusya\\Images\\903293343.JPEG"
]
display_images(image_paths)

