import socket
import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw
import math
import time
import os

drawing = False
current_color = "#525252"
drawn_lines = []
zoom_factor = 1
line_width = 1

# Set canvas size
image = None
canvas_height = 540
canvas_width = 960

# Set window size
window_width = 1920
window_height = 1080
windows_size = str(window_width) + "x" + str(window_height)

paint_drop_down_status = "up"
lighting_drop_down_status = "up"


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
        global image, zoom_factor, pan_x, pan_y, drawn_lines, draw
        # reset panning values
        pan_x = 0
        pan_y = 0
        canvas.delete("all")  # Remove all items from the canvas
        drawn_lines = []  # clears the drawn lines
        # Open the selected image using PIL (Pillow) library
        image = Image.open(file_path)
        image.thumbnail((canvas_width + 5, canvas_height + 5))  # Resize the image to fit the canvas
        draw = ImageDraw.Draw(image)  # allow for drawing on image
        zoom_factor = 1
        photo = ImageTk.PhotoImage(image)  # Convert the image to a PhotoImage object to display in a Tkinter Canvas

        # Display the image on the canvas
        canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        canvas.image = photo  # Keep a reference to the image to prevent it from being garbage collected
        update_image()

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
    x = ((event.x-pan_x)/zoom_factor)
    y = ((event.y-pan_y)/zoom_factor)
    if prev_x is not None and drawing is True:
        draw.ellipse([prev_x - line_width / 4, prev_y - line_width / 4, prev_x + line_width / 4, prev_y + line_width / 4], fill=current_color)
        while prev_x != x or prev_y != y:  # Draw a line using a series of circles
            if abs(x-prev_x) < 0.6 and abs(y-prev_y) < 0.6:  # If the two points are close enough together, snap to the last point
                draw.ellipse([x - line_width / 4, y - line_width / 4, x + line_width / 4, y + line_width / 4], fill=current_color)
                prev_x, prev_y = x, y
            else:
                # find the unit vector between the two current points
                unit_x = x-prev_x
                unit_y = y-prev_y
                magnitude = math.sqrt(unit_x**2+unit_y**2)
                unit_vector = ((unit_x/magnitude)*0.5, (unit_y/magnitude)*0.5) # 0.5 is random. it just looks good at that scale.
                # using the unit vector, progress forward one pixel and draw a circle
                next_x = prev_x + unit_vector[0]
                next_y = prev_y + unit_vector[1]
                draw.ellipse([next_x - line_width / 4, next_y - line_width / 4, next_x + line_width / 4, next_y + line_width / 4], fill=current_color)
                prev_x = next_x
                prev_y = next_y

        update_image()
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


def hex_to_rgb(hex_color):
    # Remove the #
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b

def zoom(event):
    """Function to zoom in on the image"""
    global zoom_factor
    #  If you scroll up, and you're not at max zoom
    if event.delta > 0 and zoom_factor < 2.0:
        zoom_factor += 0.1
        update_image()
    #  If you scroll down, and you're not at min zoom
    if event.delta < 0 and zoom_factor > 0.2:
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
        global pan_x, pan_y, zoom_factor
        dx = event.x - canvas.start_x
        dy = event.y - canvas.start_y
        canvas.start_x = event.x
        canvas.start_y = event.y
        pan_x += dx / zoom_factor
        pan_y += dy / zoom_factor
        update_image()


def update_image():
    """Function to update the displayed image based on the current zoom factor"""
    if image:
        resized_image = image.copy()
        resized_image = resized_image.resize((int(image.width * zoom_factor), int(image.height * zoom_factor)))
        photo = ImageTk.PhotoImage(resized_image)
        canvas.create_image(pan_x, pan_y, image=photo, anchor=tk.NW)
        canvas.image = photo
    background= Image.open("C:/Users/jmaso/PycharmProjects/ImageManipulation/background.png")
    tk_background = ImageTk.PhotoImage(background)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_background)
    canvas.bg_image = tk_background


def change_line_width(value):
    global line_width
    line_width = int(value)


def swap_drop_down():
    global paint_drop_down_status
    current_y = drop_down.winfo_y()
    if paint_drop_down_status == "up":
        paint_select_button.config(text="^")
        drop_down.place_configure(y=current_y+5)
        window.update_idletasks()
        current_y = drop_down.winfo_y()
    if paint_drop_down_status == "down":
        paint_select_button.config(text="v")
        drop_down.place_configure(y=current_y-5)
        window.update_idletasks()
        current_y = drop_down.winfo_y()
    if -230 < current_y < 105:
        window.after(1, swap_drop_down)
    elif paint_drop_down_status == "down":
        paint_drop_down_status = "up"
    elif paint_drop_down_status == "up":
        paint_drop_down_status = "down"



def open_lighting_menu():
    global lighting_drop_down_status
    if lighting_drop_down_status == "up":
        lighting_drop_down.place_configure(y=105)
    if lighting_drop_down_status == "down":
        lighting_drop_down.place_configure(y=-205)
    if lighting_drop_down_status == "down":
        lighting_drop_down_status = "up"
        lighting_select_button.config(text="v")
    elif lighting_drop_down_status == "up":
        lighting_drop_down_status = "down"
        lighting_select_button.config(text="^")


def convert_color():
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8888))

    # Send the (r, g, b) tuple to the server
    client_socket.send(','.join(map(str, hex_to_rgb(current_color))).encode())

    # Receive the response from the server
    response = client_socket.recv(1024)
    print(response)
    cmyk_color = tuple(map(float, response.decode().split(',')))

    # Close the connection
    client_socket.close()
    C = round(cmyk_color[0],2)
    M = round(cmyk_color[1],2)
    Y = round(cmyk_color[2],2)
    K = round(cmyk_color[3],2)
    CMYK_label.config(text="C:"+str(C)+", M:"+str(M)+", Y:"+str(Y)+", K:"+str(K))

# Create a Tkinter window
window = tk.Tk()
window.configure(bg="#393939")  # Set the background color to grey
window.title("Image Drawing App")
window.geometry(windows_size)

# initial panning values
panning = False
pan_x = 0
pan_y = 0

# Create the drop-down paint menu
drop_down = tk.Canvas(window, width=window_width, height=335, highlightthickness=0, bg=rgb_to_hex(217,217,217))
drop_down.place(x=0, y=-230)

# Create the top menu bar
menu_color = rgb_to_hex(50, 50, 50)
menu_bar = tk.Canvas(window, width=window_width, height=65, highlightthickness=0, bg=menu_color)
menu_bar.pack(anchor='nw')

# Create the paint select bar
paint_select_bar = tk.Canvas(window, width=window_width, height=40, highlightthickness=0, bg="#393939")
paint_select_bar.pack(anchor='nw')

# Create a button to activate the paint drop-down menu
paint_select_button = tk.Button(window, text="v", command=swap_drop_down)
paint_select_button.place(in_=paint_select_bar, relx=0.1, rely=0.2)

# Create a button to activate the lighting drop-down menu
lighting_select_button = tk.Button(window, text="v", command=open_lighting_menu)
lighting_select_button.place(in_=paint_select_button, relx=1, rely=0, x=418, y=-4)

# Create the lighting menu
lighting_drop_down = tk.Canvas(window, width=300, height=205, highlightthickness=0, bg=rgb_to_hex(235,235,235))
lighting_drop_down.place(x=340, y=-205)

# Create a canvas with a fixed size of 500x500 and place it at the top right
canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="#393939", highlightthickness=0, relief=tk.SOLID)  # Add a border outline
canvas.place(in_=drop_down, x=window_width-canvas_width-25, rely=1, y=10)
update_image()

# Create a button to open an image and place it under the canvas
open_button = tk.Button(window, text="Open Image", command=open_image)
open_button.place(in_=canvas, relx=0, rely=.8, x=-180)

# Create a button to open the color chooser and set the drawing color
color_button = tk.Button(window, text="Choose Color", command=choose_color)
color_button.place(in_=open_button, relx=0, rely=0, x=-4, y=-38)

# Create a canvas to display the current color as a solid box
color_box = tk.Canvas(window, width=75, height=27, bg=current_color, highlightthickness=0)
color_box.place(in_=color_button, relx=1, rely=0, x=4, y=-5)

# Create a slider for adjusting line width
line_width_slider = tk.Scale(window, from_=1, to=30, orient=tk.HORIZONTAL, label="Line Width", length=154, resolution=1, command=change_line_width)
line_width_slider.place(in_=open_button, relx=0, rely=0, x=-4, y=-108)

# Convert Color Button
convert_button = tk.Button(window, text="Convert Color", command=convert_color)
convert_button.place(x=200, y=700)

# Converted Color Output
CMYK_label = tk.Label(window, text="C:, M:, Y:, K:")
CMYK_label.place(in_=convert_button, relx=0, rely=0, x=-4, y=25)

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
