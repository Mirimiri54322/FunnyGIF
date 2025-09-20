import os
import time
from PIL import Image, ImageSequence # Documentation at https://pillow.readthedocs.io/en/stable/
from termcolor import colored, cprint # Documentation at https://pypi.org/project/termcolor/

DEBUG = False

test_gif = "mr-noodles-my-honest-reaction.gif"
frames = []
colors = []
rendered = []
duration = 0
width = 0
height = 0
term_cols = 0
term_rows = 0

def debug(string):
    if DEBUG:
        print(string)

# Resize the gif to fit comfortably in the terminal.
def resize(gif):
    global term_cols, term_rows

    gif_width = gif.width
    gif_height = gif.height
    debug("GIF is " + str(gif_width) + " x " + str(gif_height) + ".")

    terminal_size = os.get_terminal_size()
    term_cols = terminal_size[0]
    term_rows = terminal_size[1]
    debug(terminal_size)
    if gif_width > term_cols:
        debug("Resizing GIF to fit horizontal space...")
        scale = term_cols / gif_width
        gif = gif.resize([int(scale * gif_width), int(scale * gif_height)])
        gif_width = gif.width
        gif_height = gif.height
    if gif_height > term_rows:
        debug("Resizing GIF to fit vertical space...")
        scale = term_rows / gif_height
        gif = gif.resize([int(scale * gif_width), int(scale * gif_height)])

    debug("GIF is now " + str(gif_width) + " x " + str(gif_height) + ".")
    return gif

# Initialize all frames.
def get_frames(gif):
    ImageSequence.all_frames(gif)
    for frame in ImageSequence.Iterator(gif):
        copy = frame.copy()
        copy = frame.convert(mode="RGBA")
        copy = frame.convert(mode="P")
        copy = resize(copy)
        frames.append(copy)
    debug("Frames: " + str(len(frames)))

# Initialize all colors.
def get_colors(frames):
    for frame in frames:
        frame_colors = []
        palette = frame.getpalette(rawmode='RGBA')
        debug("Raw palette: " + str(palette))
        values_per_color = 4
        if palette == None:
            colors.append(colors[-1])
            continue

        if DEBUG:
            if int(len(palette) / values_per_color) * values_per_color != len(palette):
                print("ERROR: Color values are being left out!")

        for i in range(int(len(palette) / values_per_color)):
            color = []
            for j in range(values_per_color):
                color.append(palette[i * values_per_color + j])
            frame_colors.append(color)

        colors.append(frame_colors)
    debug("Colors: " + str(colors))

# Render one frame of a gif.
def render_frame(frame_index, frame, width, height):
    text = ""
    for row in range(height):
        for col in range(width):
            text += render_pixel(frame_index, frame[col + row * width])
        text += colored("\n")
    return text[0:-2] # Trim off the final \n.

# Render one pixel of one frame of a gif.
def render_pixel(frame_index, pixel):
    color = (colors[frame_index][pixel][0], colors[frame_index][pixel][1], colors[frame_index][pixel][2])
    attributes = []
    text = colored("  ", color, on_color=color, attrs=attributes)
    if DEBUG:
        text = colored(str(pixel) + " ", (255 - colors[frame_index][pixel][0], 255 - colors[frame_index][pixel][1], 255 - colors[frame_index][pixel][2]), on_color=color, attrs=attributes)

    # If it should be transparent.
    if not DEBUG:
        if len(colors[frame_index][pixel]) == 4:
            if colors[frame_index][pixel][3] < 128:
                text = colored("  ", attrs=attributes)

    return text

# Render the whole gif into a list of printable text frames.
def render_all():
    frame_index = 0
    for frame in frames:
        rendered.append(render_frame(frame_index, list(frame.getdata()), width, height))
        frame_index += 1

# If the terminal was resized, return True.
def is_terminal_size_different():
    terminal_size = os.get_terminal_size()
    return term_rows != terminal_size[1] or term_cols != terminal_size[0]

def initialize():
    global frames, colors, rendered, duration, width, height

    frames = []
    colors = []
    rendered = []

    gif = Image.open(test_gif)
    duration = gif.info["duration"]
    get_frames(gif)
    width = frames[0].width
    height = frames[0].height
    get_colors(frames)
    render_all()

initialize()
while True:
    if is_terminal_size_different():
            initialize()
    frame_index = 0
    for frame in rendered:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(frame, sep="", end="")
        frame_index += 1
        time.sleep(duration * 0.001)