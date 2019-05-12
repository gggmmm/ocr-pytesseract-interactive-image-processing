import tkinter as tk
import subprocess as sp
import time
from PIL import Image, ImageTk
import pytesseract

size = 100
threshold = 50
brightness = 0
contrast = 0
NUM_OF_ITERATIONS = 10
last_command = []
input_dir = './'
input_file = 'test.png'
infi = input_dir+input_file
output_dir = './'
output_file = 'test_output.png'
outfi = output_dir+output_file
border = '3x3'
bordercolor = 'White'

assert infi != outfi

def updateImage():
    global w
    global size
    global threshold
    global brightness
    global contrast
    global border
    global bordercolor
    global last_command
    global infi
    global outfi
    
    s0 = time.time()
    last_command = ['convert', infi, '-resize', str(size)+'%', '-brightness-contrast', str(brightness)+'x'+str(contrast), '-threshold', str(threshold)+'%', '-border',border,'-bordercolor', bordercolor, outfi]
    sp.call(last_command)
    
    s1 = time.time()
    
    read = pytesseract.image_to_string(Image.open(outfi))
    s2 = time.time()
    
    
    h = w.nametowidget('tesseract')
    h.config(text=read)
    
    h = w.nametowidget('exectime_convert')
    h.config(text=str(s1-s0))
    
    h = w.nametowidget('exectime_pytess')
    h.config(text=str(s2-s1))
    
    # redraw update image
    # destroy old
    h = w.nametowidget('img_label')
    h.destroy()
    
    #create new
    global img2
    img2 = tk.PhotoImage(file=outfi)
    l = tk.Label(w, image=img2, name='img_label')
    l.pack()

def updateThreshold(value):
    global threshold
    threshold = value
    updateImage()
    
def updateSize(value):
    global size
    size = value
    updateImage()
    
def updateContrast(value):
    global contrast
    contrast = value
    updateImage()

def updateBrightness(value):
    global brightness
    brightness = value
    updateImage()

def updateBorder(value):
    global border
    border = str(value)+'x'+str(value)
    updateImage()

def check_timings():
    global w
    global NUM_OF_ITERATIONS
    global last_command
    global outfi
    
    h = w.nametowidget('num_of_iterations_text')
    NUM_OF_ITERATIONS = int(h.get('current linestart', tk.END))
    
    avg_convert = 0
    avg_tesseract = 0
    for i in range(NUM_OF_ITERATIONS):
        s = time.time()
        sp.call(last_command)
        
        s1 = time.time()
        
        read = pytesseract.image_to_string(Image.open(outfi))
        s2 = time.time()
        
        avg_convert += s1-s
        avg_tesseract += s2-s1
    
    avg_convert     /= NUM_OF_ITERATIONS
    avg_tesseract   /= NUM_OF_ITERATIONS
    
    h = w.nametowidget('exectime_convert')
    h.config(text=str(avg_convert))
    
    h = w.nametowidget('exectime_pytess')
    h.config(text=str(avg_tesseract))    

w = tk.Tk()

sp.call(['convert', infi, outfi])

# time to invoke the 'convert' function and execute it
exectime_convert = tk.Label(w, text='', name='exectime_convert', font='Helvetica 16')
exectime_convert.pack()

# time to execute pytesseract image_to_string, i.e. read the image
exectime_pytess = tk.Label(w, text='', name='exectime_pytess', font='Helvetica 16')
exectime_pytess.pack()

check_timings_btn = tk.Button(w, text='Check timings with following amount of iterations', name='check_timings_btn', command=check_timings)
check_timings_btn.pack()

num_of_iterations = tk.Text(w, name='num_of_iterations_text', width=4, height=1)
num_of_iterations.insert(tk.END, str(NUM_OF_ITERATIONS))
num_of_iterations.pack()

# ======== SCALES ========
sre = tk.Scale(w, relief=tk.FLAT, orient=tk.HORIZONTAL, length=300, resolution=25, from_=100, to=1000, tickinterval=900, command=updateSize)
sre.set(200)
sre.pack()

sth = tk.Scale(w, orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=100, tickinterval=100, command=updateThreshold)
sth.set(85)
sth.pack()

sbr = tk.Scale(w, orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=updateBrightness)
sbr.set(-42)
sbr.pack()

sco = tk.Scale(w, orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=updateContrast)
sco.set(100)
sco.pack()

sbo = tk.Scale(w, orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=10, tickinterval=10, command=updateBorder)
sbo.set(3)
sbo.pack()

# pytesseract output
tesseract = tk.Label(w, text='', name='tesseract', font='Helvetica 16')
tesseract.pack()

img = tk.PhotoImage(file=infi)
l = tk.Label(w, image=img)
l.pack()

img2 = tk.PhotoImage(file=outfi)
l2 = tk.Label(w, image=img2, name='img_label')
l2.pack()

w.mainloop()
