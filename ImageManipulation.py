import pygame
from pygame.locals import *
from PIL import Image
import io
import tkinter as tk
from tkinter import filedialog
import math

pygame.init()  # Initialize Pygame

width, height = 1920, 1080  # Make this adaptive later on
screen = pygame.display.set_mode((width, height))  # Create a Pygame window
file_path = "C:/Users/jmaso/Downloads/New folder/2.png"  # Default picture

image = Image.open(file_path)
image_width, image_height = image.size  # Get the size of the image

# Resize based on display area.
size_factor = 1000 / max(image_width, image_height)
image = image.resize((math.floor(image_width * size_factor), math.floor(image_height * size_factor)))
image_width, image_height = image.size

screen.fill((255, 255, 255))  # Clear screen

# Put PIL image onto a Pygame surface
image_surface = pygame.image.load(file_path)
image_surface = pygame.transform.scale(image_surface, (image_width, image_height))

# Make an outline for the image editor
image_rect = image_surface.get_rect()
image_rect.x = 5
image_rect.y = 5
screen.blit(image_surface, image_rect)

black_box = pygame.Rect(0, 0, 1010, 1010)
pygame.draw.rect(screen, (0, 0, 0), black_box)
white_box = pygame.Rect(5, 5, 1000, 1000)
pygame.draw.rect(screen, (255, 255, 255), white_box)

drawing = False
last_pos = None
pen_color = (255, 0, 0)  # Initial pen color
eyedropper_active = False

font = pygame.font.Font(None, 36)
text = ""
input_active = False


def change_image():
    """Changes the current image being edited"""
    global image, image_surface, width, height, screen
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path)
        image_width, image_height = image.size  # Get the size of the image
        size_factor = 1000 / max(image_width, image_height)
        image = image.resize((math.floor(image_width * size_factor), math.floor(image_height * size_factor)))
        image_width, image_height = image.size

        screen.fill((255, 255, 255))
        image_surface = pygame.image.load(file_path)  # Convert the PIL image to Pygame surface
        image_surface = pygame.transform.scale(image_surface, (image_width, image_height))

        # Make an outline for the image editor
        black_box = pygame.Rect(0, 0, 1010, 1010)
        pygame.draw.rect(screen, (0, 0, 0), black_box)
        white_box = pygame.Rect(5, 5, 1000, 1000)
        pygame.draw.rect(screen, (255, 255, 255), white_box)

        image_rect = image_surface.get_rect()
        image_rect.x = 5
        image_rect.y = 5
        screen.blit(image_surface, image_rect)  # Display the image


# Create a button to change the image
change_image_button = pygame.Rect(10, 80, 195, 40)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # click to start drawing
                drawing = True
                last_pos = event.pos
            if event.button == 3:  # Right click for eyedropper
                eyedropper_active = True
            if event.button == 1:  # check if the current color box is clicked
                current_color_box = pygame.Rect(10, 10, 60, 60)
                if current_color_box.collidepoint(event.pos):
                    input_active = not input_active
            if change_image_button.collidepoint(event.pos):  # Check if the change image button is clicked
                change_image()

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:  # stop drawing
                drawing = False
                last_pos = None
            if event.button == 3:  # deactivate eyedropper
                eyedropper_active = False
        elif event.type == MOUSEMOTION:
            if drawing:
                current_pos = event.pos
                if last_pos:
                    pygame.draw.line(image_surface, pen_color, last_pos, current_pos, 5)
                last_pos = current_pos
        elif event.type == KEYDOWN:
            if input_active:
                if event.key == K_RETURN:
                    try:
                        pen_color = tuple(map(int, text.split(',')))
                    except ValueError:
                        pass
                    text = ""
                    input_active = False
                elif event.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    # Eyedropper tool
    if eyedropper_active:
        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            pixel_color = image.getpixel(mouse_pos)
            pen_color = pixel_color

    # Display changes
    screen.blit(image_surface, image_rect)

    # Display the current pen color as a square
    current_color_box = pygame.Rect(10, 10, 60, 60)  # Square current color box
    pygame.draw.rect(screen, pen_color, current_color_box)

    if input_active:
        input_box = pygame.Rect(current_color_box.right + 10, current_color_box.y, 235, 32)
        pygame.draw.rect(screen, (0, 0, 0), input_box)
        text_surface = font.render("R,G,B: " + text, True, (255, 255, 255))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

    # Draw the change image button
    pygame.draw.rect(screen, (0, 128, 0), change_image_button)  # Draw Rectangle
    change_image_text = font.render("Change Image", True, (255, 255, 255))
    screen.blit(change_image_text, (change_image_button.x + 10, change_image_button.y + 5))  # Draw Text

    pygame.display.update()

pygame.quit()
