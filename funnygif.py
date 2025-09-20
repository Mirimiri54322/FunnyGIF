import os
from PIL import Image, ImageSequence # Documentation at https://pillow.readthedocs.io/en/stable/
from termcolor import colored, cprint # Documentation at https://pypi.org/project/termcolor/

DEBUG = True

test_gif = "ca2l_talk.gif"
frames = []
colors = []

def debug(string):
    if DEBUG:
        print(string)

# Resize the gif to fit comfortably in the terminal.
def resize(gif):
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
        frames.append(list(frame.getdata()))
    debug("Frames: " + str(len(frames)))

# Initialize all colors.
def get_colors(gif):
    for frame in frames:
        frame_colors = []
        transparency = gif.has_transparency_data
        palette = gif.getpalette()
        debug("Raw palette: " + str(palette))
        values_per_color = 3
        if transparency:
            values_per_color += 1

        if DEBUG:
            if int(len(palette) / values_per_color) * values_per_color != len(palette):
                print("ERROR: Color values are being left out!")

        for i in range(int(len(palette) / values_per_color)):
            color = []
            for j in range(values_per_color):
                color.append(palette[i * values_per_color + j])
            frame_colors.append(color)

        if DEBUG:
            for i in range(len(frame_colors)):
                for j in range(len(frame_colors)):
                    if i >= j:
                        continue
                    if frame_colors[i] == frame_colors[j]:
                        print("ERROR: Two color values were the same!")

        colors.append(frame_colors)
    debug("Colors: " + str(colors))

# Render one frame of a gif.
def render_frame(current_frame, frame, width, height):
    for row in range(height):
        for col in range(width):
            render_pixel(current_frame, frame[col + row * width])
        print("")

# Render one pixel of one frame of a gif.
def render_pixel(current_frame, pixel):
    color = (colors[current_frame][pixel][0], colors[current_frame][pixel][1], colors[current_frame][pixel][2])
    attributes = []
    text = colored("██", color, on_color=color, attrs=attributes)
    if DEBUG:
        text = colored(str(pixel) + " ", (colors[current_frame][pixel][1], colors[current_frame][pixel][2], colors[current_frame][pixel][0]), on_color=color, attrs=attributes)

    # If it should be transparent.
    if len(colors[current_frame][pixel]) == 4:
        if colors[current_frame][pixel][3] != 0:
            attributes.append("blink")
            text = colored("  ", attrs=attributes)

    print(text, sep="", end="")

original = Image.open(test_gif)
gif = original.copy()
gif = resize(gif)
width = gif.width
height = gif.height
get_frames(gif)
get_colors(gif)
# while True:
current_frame = 0
for frame in frames:
    render_frame(current_frame, frame, width, height)
    current_frame += 1