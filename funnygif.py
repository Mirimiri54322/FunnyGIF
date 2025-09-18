from PIL import Image, ImageSequence
from termcolor import colored, cprint

DEBUG = True

test_gif = "ca2l_talk.gif"
frames = []

def debug(string):
    if DEBUG:
        print(string)

# Initialize all frames.
def get_frames(gif):
    ImageSequence.all_frames(gif)
    for frame in ImageSequence.Iterator(gif):
        frames.append(frame)

# Render one frame of a gif.
def render_frame(frame):
    for row in range(frame.height):
        for col in range(frame.width):
            render_pixel(frame[row, col])

# Render one pixel of one frame of a gif.
def render_pixel(pixel):
    print(pixel)

gif = Image.open(test_gif)
get_frames(gif)
while True:
    for frame in frames:
        render_frame(frame)