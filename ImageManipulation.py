import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw

drawing = False
current_color = "#525252"
drawn_lines = []
zoom_factor = 1
prev_zoom_factor = 1

# Set canvas size
image = None
canvas_height = 540
canvas_width = 960

# Set window size
window_width = 1920
window_height = 1080
windows_size = str(window_width) + "x" + str(window_height)


def choose_color():
    """Function to open the color chooser and update the drawing color"""
    global current_color
    color = colorchooser.askcolor(initialcolor=current_color)[1]  # Ask the user to select a color
    if color:
        current_color = color
        color_box.config(bg=current_color)  # Change the background color to the selected color


def open_image():
    """Function to open an image file and display it on a canvas"""
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.ppm")])
    if file_path:
        global image, zoom_factor, pan_x, pan_y, drawn_lines, prev_zoom_factor, prev_pan_x, prev_pan_y, draw
        # reset panning values
        pan_x = 0
        pan_y = 0
        prev_pan_x = 0
        prev_pan_y = 0
        canvas.delete("all")  # Remove all items from the canvas
        drawn_lines = []  # clears the drawn lines
        # Open the selected image using PIL (Pillow) library
        image = Image.open(file_path)
        image.thumbnail((canvas_width + 5, canvas_height + 5))  # Resize the image to fit the canvas
        draw = ImageDraw.Draw(image)  # allow for drawing on image
        zoom_factor = 1
        prev_zoom_factor = 1
        photo = ImageTk.PhotoImage(image)  # Convert the image to a PhotoImage object to display in a Tkinter Canvas

        # Display the image on the canvas
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo  # Keep a reference to the image to prevent it from being garbage collected

def start_draw(event):
    global drawing, prev_x, prev_y
    drawing = True
    prev_x = None
    prev_y = None


def stop_draw(event):
    global drawing, prev_x, prev_y
    drawing = False
    prev_x = None
    prev_y = None


def draw(event):
    """Function to draw connected lines on the canvas"""
    global prev_x, prev_y
    x, y = event.x, event.y
    if prev_x is not None and drawing is True:
        draw.line([prev_x, prev_y, x, y], fill=current_color, width=2)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo  # Keep a reference to the image to prevent it from being garbage collected
    prev_x, prev_y = x, y

def eyedropper(event):
    global last_x, last_y, current_color
    if image:
        # Get the color from the image at the clicked position
        image_x = (event.x - pan_x) / zoom_factor
        image_y = (event.y - pan_y) / zoom_factor
        eyedropper_color = image.getpixel((image_x, image_y))
        current_color = rgb_to_hex(eyedropper_color[0], eyedropper_color[1], eyedropper_color[2])
        color_box.config(bg=current_color)  # Change the background color to the selected color


def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def zoom(event):
    """Function to zoom in on the image"""
    global prev_zoom_factor, zoom_factor
    #  If you scroll up, and you're not at max zoom
    if event.delta > 0 and zoom_factor < 2.0:
        prev_zoom_factor = zoom_factor
        zoom_factor += 0.1
        update_image()
    #  If you scroll down, and you're not at min zoom
    if event.delta < 0 and zoom_factor > 0.2:
        prev_zoom_factor = zoom_factor
        zoom_factor -= 0.1
        update_image()


def start_pan(event):
    """Function to start panning"""
    global panning, pan_x, pan_y
    canvas.start_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    canvas.start_y = canvas.winfo_pointery() - canvas.winfo_rooty()
    panning = True
    canvas.config(cursor="fleur")


def stop_pan(event):
    """Function to stop panning"""
    global panning
    panning = False
    canvas.config(cursor="")


def pan(event):
    """Function to handle panning"""
    if panning:
        global pan_x, pan_y, prev_pan_x, prev_pan_y, zoom_factor
        dx = event.x - canvas.start_x
        dy = event.y - canvas.start_y
        canvas.start_x = event.x
        canvas.start_y = event.y
        pan_x += dx / zoom_factor
        pan_y += dy / zoom_factor
        update_image()
        prev_pan_x = pan_x
        prev_pan_y = pan_y


def update_image():
    """Function to update the displayed image based on the current zoom factor"""
    global prev_zoom_factor
    if image:
        resized_image = image.copy()
        resized_image = resized_image.resize((int(image.width * zoom_factor), int(image.height * zoom_factor)))
        photo = ImageTk.PhotoImage(resized_image)
        canvas.create_image(pan_x, pan_y, image=photo, anchor=tk.NW)
        canvas.image = photo


# Create a Tkinter window
window = tk.Tk()
window.configure(bg="#393939")  # Set the background color to grey
window.title("Image Drawing App")
window.geometry(windows_size)

# initial panning values
panning = False
pan_x = 0
pan_y = 0
prev_pan_x = 0
prev_pan_y = 0

# Create a canvas with a fixed size of 500x500 and place it at the top right
canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="#393939", highlightbackground="#4F555C",
                   relief=tk.SOLID)  # Add a border outline
canvas.place(x=window_width - canvas_width - 10, y=10)  # Position the canvas at the top right with 10 pixels of padding

# Create a button to open an image and place it under the canvas
open_button = tk.Button(window, text="Open Image", command=open_image)
open_button.place(in_=canvas, relx=0, rely=.8, x=-180)

# Create a button to open the color chooser and set the drawing color
color_button = tk.Button(window, text="Choose Color", command=choose_color)
color_button.place(in_=open_button, relx=0, rely=0, x=-4, y=-38)

# Create a canvas to display the current color as a solid box
color_box = tk.Canvas(window, width=75, height=22, bg=current_color, highlightbackground="#393939")
color_box.place(in_=color_button, relx=1, rely=0, x=4, y=-5)

# Bind the canvas to zoom
canvas.bind("<MouseWheel>", zoom)

# Bind the canvas to the draw function
canvas.bind("<Button-1>", start_draw)
canvas.bind("<ButtonRelease-1>", stop_draw)
canvas.bind("<B1-Motion>", draw)


# Bind the canvas to mouse events for panning
canvas.bind("<Button-2>", start_pan)
canvas.bind("<ButtonRelease-2>", stop_pan)
canvas.bind("<Motion>", pan)

canvas.bind("<Button-3>", eyedropper)

# Start the Tkinter main loop
window.mainloop()
