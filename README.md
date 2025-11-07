# FunnyGIF
 Put a funny GIF in your terminal.

## Usage
Run funnygif with the filename of a GIF, and optionally, arguments. For example, "funnygif.py wizard.gif speed=1.5"
On Linux, you can copy the file "funnygif" into your /usr/local/bin folder, and change the file path to the place where funnygif.py is located to call it from anywhere with just "funnygif".

## Arguments
Each argument is shown with its name and its default value, and a description of what it does.
- char (char=" ") The one or two characters used to draw each pixel of the image. By default, the image renders pixels as two spaces with colored backgrounds.
- colors (colors= however many colors the image has by default) Limits the maximum number of colors to the specified value. Setting this to more colors than the image has will not produce a visible result.
- dither (dither=true) "true" or "false" for whether or not the image should be dithered. Only does anything if colors is set. It may be hard to notice the effect of this option.
- palette (palette=none) Designates a global palette to be used for all frames. Each pixel becomes the closest color from the palette. Presets: none, ace, agender, aro, aroace, bi, bw, catpuccin, cmyk, demiboy, demigirl, disability, dracula, gay, genderfluid, genderqueer, intersex, lesbian, monochrome, nonbinary, paint, pan, polyamory, polysexual, queerplatonic, rgb, rgbcmy, tertiary, trans, vaporwave.
- reverse (reverse=false) "true" or "false" for whether or not to play the animation backwards.
- speed (speed=1.0) A higher speed makes the GIF animate faster, and a lower speed makes it slower.

## Feature Wishlist
- Option to use predefined color palettes. So, like, changing all the colors to the closest one in a predefined set.
- Option to force the same color palette on every frame (not predefined; generated based on the image and the colors in it).
- Fix tearing that appears with larger images on larger screens.
- Option to flip image.
- Option to rotate image.
- Option to automatically crop off pixels that are transparent on all frames.
- Option to resize image.
- Option to pixellate image more (4 "pixel" segments instead of 1 "pixel" segments).
- Option to scale down the number of frames by a constant factor. For instance, to take out every other frame.