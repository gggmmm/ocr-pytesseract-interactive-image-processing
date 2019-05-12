# pytesseract-interactive-filtering
Simple GUI-based script to help you best pre-filter your image before being read by pytesseract.

![alt text](screen.png "App screenshot")

1. Time to execute the 'convert' function from ImageMagick.
2. Time to execute pytesseract.text\_to\_string.
3. Set the number of iterations, then by clicking the above button, that amount of times the 'convert' and pytesseract functions will be invoked. The average execution timings are then presented in labels 1 and 2.
4. Set '-resize' %. 100= unchanged, 1000=10 times bigger.
5. Set '-threshold' in %.
6. Set brightness in '-brightness-contrast'.
7. Set contrast in '-brightness-contrast'.
8. Set border '-border'. E.g. 3= a 3pixel by 3pixel white border. This one is hard to see in the app, but check the output file to see it better.
9. What pytesseract is currently reading.
10. The input image.
11. The modified image.

Suggestion: the resize slider (the first) is best used when clicking on the dark area. Instead, if you slide by grabbing the slider the interface gets messy.

Tested with:
- linux mint
- python 3.6.7
- Pillow 6.0.0
- pytesseract 0.2.6
- TkInter 8.6
