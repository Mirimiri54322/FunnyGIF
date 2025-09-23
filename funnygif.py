import os
import sys
import time
from PIL import Image, ImageSequence # Documentation at https://pillow.readthedocs.io/en/stable/
from termcolor import colored, cprint # Documentation at https://pypi.org/project/termcolor/

# Debug constants.
DEBUG = False
SHOULD_PLAY = True

VALUES_PER_COLOR = 4 # In RGBA, there will be 4 colors.

frames = []
colors = []
rendered = []
duration = 0
width = 0
height = 0
term_cols = 0
term_rows = 0

# argv[1] should always be the file to use.
gif_file = None

# Arg: Character to use to draw the image.
character = None

# Arg: whether or not to dither the image when shrinking.
is_dithered = True

# Arg: the integer number of colors to have in the palette. If this is None, use as many colors as the image has by default.
max_colors = None

# Arg: the constant by which to multiply the speed of the GIF at playback.
speed = 1.0

def debug(string):
    if DEBUG:
        print(string)

# Resize the frame to fit comfortably in the terminal.
def resize(frame):
    global term_cols, term_rows

    # Get the size of the frame.
    frame_width = frame.width
    frame_height = frame.height
    debug("Frame is initially " + str(frame_width) + " x " + str(frame_height) + ".")

    # Get the size of the terminal.
    terminal_size = os.get_terminal_size()
    debug(terminal_size)
    term_cols = terminal_size[0]
    term_rows = terminal_size[1]

    # Resize if necessary.
    if frame_width > term_cols:
        debug("Resizing frame to fit horizontal space...")
        scale = term_cols / frame_width
        frame = frame.resize([int(scale * frame_width), int(scale * frame_height)])
        frame_width = frame.width
        frame_height = frame.height
    if frame_height > term_rows:
        debug("Resizing frame to fit vertical space...")
        scale = term_rows / frame_height
        frame = frame.resize([int(scale * frame_width), int(scale * frame_height)])
        frame_width = frame.width
        frame_height = frame.height

    debug("Frame is now " + str(frame_width) + " x " + str(frame_height) + ".")
    return frame

# Initialize all frames.
def get_frames(gif):
    global frames

    ImageSequence.all_frames(gif)
    for frame in ImageSequence.Iterator(gif):
        copy = frame.copy()

        # Cut the number of colors, if that's what the user wanted.
        if max_colors != None:
            if is_dithered:
                frame = frame.quantize(max_colors, dither=Image.Dither.FLOYDSTEINBERG)
            else:
                frame = frame.quantize(max_colors, dither=Image.Dither.NONE)

        # Convert to RGBA and then back to P (palette) so that all frames use palette mode consistently.
        copy = frame.convert(mode="RGBA")
        copy = copy.convert(mode="P")

        copy = resize(copy)
        frames.append(copy)

    debug("Frames: " + str(len(frames)))

# Initialize all colors.
def get_colors(frames):
    global colors

    # Each frame can have its own palette in some GIFs, so we must get a seperate palette for each frame.
    for frame in frames:
        frame_colors = []
        palette = frame.getpalette(rawmode='RGBA')
        debug("Raw palette: " + str(palette))

        # If there was no palette for this frame, then the palette is the same as the previous frame.
        if palette == None:
            colors.append(colors[-1])
            continue

        if DEBUG:
            if int(len(palette) / VALUES_PER_COLOR) * VALUES_PER_COLOR != len(palette):
                print("ERROR: Color values are being left out!")
                sys.exit()

        # Group the palette from a list of plain ints to a set of [[R, G, B, A], ...]
        for i in range(int(len(palette) / VALUES_PER_COLOR)):
            color = []
            for j in range(VALUES_PER_COLOR):
                color.append(palette[i * VALUES_PER_COLOR + j])
            frame_colors.append(color)

        if DEBUG:
            if max_colors != None:
                if len(frame_colors) > max_colors:
                    print("ERROR: More colors than the maximum amount specified by the user.")
                    sys.exit()

        colors.append(frame_colors)
    debug("Colors: " + str(colors))

# Render one frame of a gif as a printable string.
def render_frame(frame_index, frame, width, height):
    text = ""
    for row in range(height):
        for col in range(width):
            text += render_pixel(frame_index, frame[col + row * width])
        text += colored("\n")
    return text[0:-2] # Trim off the final \n.

# Render one pixel of one frame of a gif as a printable string.
def render_pixel(frame_index, pixel):
    global character

    color = (colors[frame_index][pixel][0], colors[frame_index][pixel][1], colors[frame_index][pixel][2])
    attributes = []

    text = colored("  ", color, on_color=color, attrs=attributes)
    if character != None:
        debug("Using alternate character " + character + " to render pixel.")
        if len(character) == 1:
            text = colored(character + character, color, attrs=attributes)
        elif len(character) == 2:
            text = colored(character, color, attrs=attributes)
    if DEBUG:
        text = colored(str(pixel) + " ", (255 - colors[frame_index][pixel][0], 255 - colors[frame_index][pixel][1], 255 - colors[frame_index][pixel][2]), on_color=color, attrs=attributes)

    # If it should be transparent, don't use any color for the foreground or background.
    if colors[frame_index][pixel][3] < 128:
        text = colored("  ", attrs=attributes)

    return text

# Render the whole gif into a list of printable strings, each representing one frame.
def render_all():
    debug("Rendering...")
    frame_index = 0
    for frame in frames:
        rendered.append(render_frame(frame_index, list(frame.getdata()), width, height))
        frame_index += 1
    debug("Render completed!")

# If the terminal was resized, return True.
def is_terminal_size_different():
    terminal_size = os.get_terminal_size()
    return term_rows != terminal_size[1] or term_cols != terminal_size[0]

def initialize():
    global frames, colors, rendered, duration, width, height, gif_file

    frames = []
    colors = []
    rendered = []

    gif = Image.open(gif_file)
    duration = gif.info["duration"]
    get_frames(gif)
    width = frames[0].width
    height = frames[0].height
    get_colors(frames)
    render_all()

# Interpret command line arguments.
def interpret_args():
    global gif_file, character, is_dithered, speed, max_colors

    if len(sys.argv) < 2:
        print("ERROR: No GIF specified! Put in the filename of the GIF you want to use, or \"help\" for more information.")
        sys.exit()

    if sys.argv[1] == "help":
        readme = open("README.md", "r").read()
        print(readme)
        sys.exit()

    gif_file = sys.argv[1]

    debug(str(len(sys.argv)) + " arguments.")
    for arg in sys.argv[2:]:
        debug(arg)

        if arg[:5] == "char=":
            character = arg[5:]
            if len(character) != 1 and len(character) != 2:
                print("ERROR: Length of char= value can only be 1 or 2.")
                sys.exit()
            debug("Set character to " + character + ".")

        elif arg[:7] == "colors=":
            max_colors = int(arg[7:])
            debug("Set max_colors to " + str(max_colors) + ".")

        elif arg[:7] == "dither=":
            if arg[7:].lower() == "true":
                is_dithered = True
            elif arg[7:].lower() == "false":
                is_dithered = False
            else:
                print("ERROR: Dither mode not recognized!")
                sys.exit()

        elif arg[:6] == "speed=":
            speed = float(arg[6:])
            debug("Set speed to " + str(speed) + ".")

interpret_args()
initialize()
if SHOULD_PLAY:
    while True:
        frame_index = 0
        for frame in rendered:
            if is_terminal_size_different():
                initialize()
                break
            os.system('cls' if os.name == 'nt' else 'clear')
            print(frame, sep="", end="")
            frame_index += 1
            time.sleep(duration * 0.001 / speed)