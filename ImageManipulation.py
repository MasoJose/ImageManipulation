import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw

# Default drawing color
current_color = "dark grey"
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
        global image, zoom_factor, pan_x, pan_y, drawn_lines, prev_zoom_factor, prev_pan_x, prev_pan_y
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
        zoom_factor = 1
        prev_zoom_factor = 1

        photo = ImageTk.PhotoImage(image)  # Convert the image to a PhotoImage object to display in a Tkinter Canvas

        # Display the image on the canvas
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo  # Keep a reference to the image to prevent it from being garbage collected


def draw(event):
    """Function to draw connected lines on the canvas"""
    x, y = event.x, event.y
    if hasattr(canvas, 'prev_x') and hasattr(canvas,
                                             'prev_y') and canvas.prev_x is not None and canvas.prev_y is not None:
        prev_x, prev_y = canvas.prev_x, canvas.prev_y
        line = canvas.create_line(prev_x, prev_y, x, y, fill=current_color, width=2 * zoom_factor, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        drawn_lines.append(line)
    canvas.prev_x, canvas.prev_y = x, y


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


def reset_prev(event):
    """Function to reset prev_x and prev_y when the mouse is no longer being clicked"""
    canvas.prev_x = None
    canvas.prev_y = None


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

    # zooming and panning lines
    old_lines = drawn_lines.copy()
    drawn_lines.clear()
    for line in old_lines:
        coords = canvas.coords(line)
        line_color = canvas.itemcget(line, 'fill')
        x1 = (coords[0] - pan_x) * (zoom_factor / prev_zoom_factor) + pan_x + (pan_x - prev_pan_x)
        y1 = (coords[1] - pan_y) * (zoom_factor / prev_zoom_factor) + pan_y + (pan_y - prev_pan_y)
        x2 = (coords[2] - pan_x) * (zoom_factor / prev_zoom_factor) + pan_x + (pan_x - prev_pan_x)
        y2 = (coords[3] - pan_y) * (zoom_factor / prev_zoom_factor) + pan_y + (pan_y - prev_pan_y)
        line = canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2 * zoom_factor, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36)
        drawn_lines.append(line)
    prev_zoom_factor = zoom_factor
    for line in old_lines:
        canvas.delete(line)


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
canvas.bind("<B1-Motion>", draw)

# Bind the canvas to the mouse release event to reset prev_x and prev_y
canvas.bind("<ButtonRelease-1>", reset_prev)

# Bind the canvas to mouse events for panning
canvas.bind("<Button-2>", start_pan)
canvas.bind("<ButtonRelease-2>", stop_pan)
canvas.bind("<Motion>", pan)

canvas.bind("<Button-3>", eyedropper)

# Start the Tkinter main loop
window.mainloop()
