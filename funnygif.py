import math
import os
import signal
import sys
import time
from PIL import Image, ImageSequence # Documentation at https://pillow.readthedocs.io/en/stable/
from termcolor import colored # Documentation at https://pypi.org/project/termcolor/

# Debug constants.
DEBUG = False
SHOULD_PLAY = True

# Non-debug constants.
VALUES_PER_COLOR = 4 # In RGBA, there will be 4 colors.

# Palette constants.
PALETTE_BI = [[214, 2, 112], [155, 79, 150], [0, 56, 168]]
PALETTE_BW = [[0, 0, 0], [255, 255, 255]]
PALETTE_CATPUCCIN = [[245, 224, 220], [242, 205, 205], [245, 194, 231], [203, 166, 247], [243, 139, 168], [235, 160, 172], [250, 179, 135], [249, 226, 175], [166, 227, 161], [148, 226, 213], [137, 220, 235], [116, 199, 236], [137, 180, 250], [180, 190, 254], [205, 214, 244], [186, 194, 222], [166, 173, 200], [147, 153, 178], [127, 132, 156], [108, 112, 134], [88, 91, 112], [69, 71, 90], [49, 50, 68], [30, 30, 46], [24, 24, 37], [17, 17, 27]]
PALETTE_CMYK = [[255, 255, 0], [255, 0, 255], [0, 255, 255], [255, 255, 255], [0, 0, 0]]
PALETTE_DRACULA = [[40, 42, 54], [68, 71, 90], [248, 248, 242], [98, 114, 164], [139, 223, 253], [80, 250, 123], [255, 184, 108], [255, 121, 198], [189, 147, 249], [255, 85, 85], [241, 250, 140]]
PALETTE_LESBIAN = [[213, 45, 0], [239, 118, 39], [255, 154, 86], [255, 255, 255], [209, 98, 164], [181, 86, 144], [181, 86, 144], [163, 2, 98]]
PALETTE_MONOCHROME = [[0, 0, 0], [64, 64, 64], [128, 128, 128], [192, 192, 192], [255, 255, 255]]
PALETTE_PAINT = [[0, 0, 0], [127, 127, 127], [136, 0, 20], [237, 28, 35], [255, 125, 39], [255, 242, 0], [34, 177, 77], [0, 162, 232], [62, 71, 203], [162, 73, 164], [255, 255, 255], [195, 195, 195], [185, 120, 88], [255, 174, 204], [255, 202, 12], [238, 229, 178], [180, 230, 29], [153, 217, 235], [112, 146, 190], [200, 191, 231]]
PALETTE_RGB = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255], [0, 0, 0]]
PALETTE_RGBCMY = [[255, 0, 0], [255, 255, 0], [0, 255, 0], [0, 255, 255], [0, 0, 255], [255, 0, 255], [0, 0, 0], [255, 255, 255]]
PALETTE_TRANS = [[91, 206, 250], [245, 169, 184], [255, 255, 255]]
PALETTE_VAPORWAVE = [[192, 255, 255], [128, 255, 255], [64, 255, 255], [0, 255, 255], [0, 0, 255], [64, 0, 255], [192, 0, 255], [255, 0, 255], [255, 64, 255], [255, 128, 255], [255, 192, 255], [128, 255, 192]]

# Image variables.
frames = []
colors = []
rendered = []
duration = 0
width = 0
height = 0
term_cols = 0
term_rows = 0

# Arg variables.
character = None # Arg: Character to use to draw the image.
gif_file = None # argv[1] should always be the file to use.
global_palette = None # Arg: the specific color palette the entire image must use. Pixels become whichever color in the palette they are closest to. If it's set to None, then no global palette is used.
is_dithered = True # Arg: whether or not to dither the image when shrinking.
is_reversed = False # Arg: whether or not to play the animation backwards.
max_colors = None # Arg: the integer number of colors to have in the palette. If this is None, use as many colors as the image has by default.
speed = 1.0 # Arg: the constant by which to multiply the speed of the GIF at playback.

# Signal variables.
is_sig_quit = False

# Print a debug message if DEBUG is turned on.
def debug(string):
    if DEBUG:
        print(string)

# Catch the quit signal to exit gracefully.
def sig_int_handler(signal, frame):
    global is_sig_quit

    debug("Received SIGQUIT.")
    is_sig_quit = True

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

    # Resize if necessary. Keep in mind that the calls to frame.resize() in here are not calls to THIS method, but calls to a PIL Image method.
    if frame_width > term_cols:
        debug("Resizing frame to fit horizontal space...")
        scale = float(term_cols) / float(frame_width)
        frame = frame.resize([int(math.trunc(scale * frame_width)), int(math.trunc(scale * frame_height))])
        frame_width = frame.width
        frame_height = frame.height
    if frame_height > term_rows:
        debug("Resizing frame to fit vertical space...")
        scale = float(term_rows) / float(frame_height)
        frame = frame.resize([int(math.trunc(scale * frame_width)), int(math.trunc(scale * frame_height))])
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

# Get the distance between two colors.
def get_color_distance(color1, color2):
    distance = 0
    for i in range(min(len(color1), len(color2))):
        distance += abs(color1[i] - color2[i])

    return distance


# Given a pixel, get the closest color from the global palette and apply it to the pixel.
def get_closest_palette_color(color):
    global global_palette

    closest_color = None
    closest_distance = None
    for current_color in global_palette:
        current_distance = get_color_distance(color, current_color)
        if closest_color == None:
            closest_color = current_color
            closest_distance = current_distance
            continue
        if current_distance < closest_distance:
            closest_color = current_color
            closest_distance = current_distance

    debug(str(color) + " was closest to " + str(closest_color) + ".")
        
    return closest_color

# Initialize all colors.
def get_colors(frames):
    global colors, global_palette

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
                sys.exit(1)

        # Group the palette from a list of plain ints to a set of [[R, G, B, A], ...]
        for i in range(int(len(palette) / VALUES_PER_COLOR)):
            color = []

            for j in range(VALUES_PER_COLOR):
                color.append(palette[i * VALUES_PER_COLOR + j])

            # Apply a global palette if one was specified.
            if global_palette != None:
                # Apply only if the pixel isn't mostly transparent.
                if VALUES_PER_COLOR == 4:
                    if color[3] > 127:
                        debug("Applying global palette " + str(global_palette) + " to frame " + str(frame) + ".")
                        closest = get_closest_palette_color(color)
                        color[0] = closest[0]
                        color[1] = closest[1]
                        color[2] = closest[2]

            frame_colors.append(color)

        if DEBUG:
            if max_colors != None:
                if len(frame_colors) > max_colors:
                    print("ERROR: More colors than the maximum amount specified by the user.")
                    sys.exit(1)

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

    if is_reversed:
        rendered.reverse()
        
    debug("Render completed!")


# If the terminal was resized, return True.
def is_terminal_size_different():
    terminal_size = os.get_terminal_size()
    return term_rows != terminal_size[1] or term_cols != terminal_size[0]

def initialize():
    global frames, colors, rendered, duration, width, height, gif_file

    # Attach the CTRL+C signal to the cleaner, custom signal handler.
    signal.signal(signal.SIGINT, sig_int_handler)

    # Make it look cleaner while it renders.
    clear_screen()
    print("...")

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
    global gif_file, global_palette, character, is_dithered, is_reversed, speed, max_colors

    if len(sys.argv) < 2:
        print("ERROR: No GIF specified! Put in the filename of the GIF you want to use, or \"help\" for more information.")
        sys.exit(1)

    if sys.argv[1] == "help":
        readme = open("README.md", "r").read()
        print(readme)
        sys.exit(0)

    gif_file = sys.argv[1]

    debug(str(len(sys.argv)) + " arguments.")
    for arg in sys.argv[2:]:
        debug(arg)

        if arg[:5] == "char=":
            character = arg[5:]
            if len(character) != 1 and len(character) != 2:
                print("ERROR: Length of char= value can only be 1 or 2.")
                sys.exit(1)
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
                sys.exit(1)

        elif arg[:8] == "palette=":
            global_palette = arg[8:]

            # Check if it's one of the presets.
            if global_palette.lower() == "none":
                global_palette = None
            elif global_palette.lower() == "bi":
                global_palette = PALETTE_BI
            elif global_palette.lower() == "bw":
                global_palette = PALETTE_BW
            elif global_palette.lower() == "cmyk":
                global_palette = PALETTE_CMYK
            elif global_palette.lower() == "catpuccin":
                global_palette = PALETTE_CATPUCCIN
            elif global_palette.lower() == "dracula":
                global_palette = PALETTE_DRACULA
            elif global_palette.lower() == "lesbian":
                global_palette = PALETTE_LESBIAN
            elif global_palette.lower() == "monochrome":
                global_palette = PALETTE_MONOCHROME
            elif global_palette.lower() == "paint":
                global_palette = PALETTE_PAINT
            elif global_palette.lower() == "rgb":
                global_palette = PALETTE_RGB
            elif global_palette.lower() == "rgbcmy":
                global_palette = PALETTE_RGBCMY
            elif global_palette.lower() == "trans":
                global_palette = PALETTE_TRANS
            elif global_palette.lower() == "vaporwave":
                global_palette = PALETTE_VAPORWAVE
            else:
                # Once custom palettes are allowed, take this error out.
                print("ERROR: Palette preset not recognized!")
                sys.exit(1)

            debug("Set global palette to " + str(global_palette) + ".")

        elif arg[:8] == "reverse=":
            is_reversed = bool(arg[8:])
            debug("Set is_reversed to " + str(is_reversed) + ".")

        elif arg[:6] == "speed=":
            speed = float(arg[6:])
            debug("Set speed to " + str(speed) + ".")

# Clear the screen.
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

interpret_args()
initialize()
if SHOULD_PLAY:
    while True:
        frame_index = 0
        for frame in rendered:
            if is_terminal_size_different():
                initialize()
                break
            if is_sig_quit:
                sys.exit(0)
            clear_screen()
            print(frame, sep="", end="")
            frame_index += 1
            time.sleep(duration * 0.001 / speed)