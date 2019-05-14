# pytesseract-interactive-filtering
Simple GUI-based script to help you best pre-filter your image before being read by pytesseract.

To process the image, 'convert' by ImageMagick is used.

![alt text](screen.png "App screenshot")

In the Display window (right):
+ First line: what pytesseract is reading from the image at the bottom.
+ Second line: original image.
+ Third line: image processed using the parameters used in window 'Controls', which is "read" by pytesseract.

In the Controls window (left) you can set the following options that affect the aforementioned 'convert' function:
+ Set '-resize' %. 100= unchanged, 1000=10 times bigger.
+ Set '-threshold' in %.
+ Set brightness in '-brightness-contrast'.
+ Set contrast in '-brightness-contrast'.
+ Set border '-border'. E.g. 3= a 3pixel by 3pixel white border. This one is hard to see in the app, but check the output file to see it better.

**Usage**: first place a file called 'test.png' in the same folder as the program, then do `python3 main.py`.

Suggestion: the slider that controls the size (resize) is best used when clicking on the dark area. Instead, if you slide by grabbing the slider the interface gets messy.

Tested with:
- linux mint 19.1
- python 3.6.7
- Pillow 6.0.0
- pytesseract 0.2.6
- TkInter 8.6
- ImageMagick 6.9.7-4 Q16

Coming soon (in order of priority/feasibility):
* ~~save current settings/load last saved settings~~
* show the full 'convert' function with all used options
* Add functions erode, dilate, open, close, smooth with shapes diamond, square, octagon disk, plus, cross, ring, rectangle ([check this out](https://www.imagemagick.org/Usage/morphology/))
* enter parameters through text-box (to avoid slow  slider)
* personalized slider-step
* ordering of the options. Currently the order is from top to bottom, but doing thresholding before resizing may make a difference
* checkbox to enable/disable each slider
