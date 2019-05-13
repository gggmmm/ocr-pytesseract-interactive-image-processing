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
    l = tk.Label(w, image=img2, name='img_label').grid(row=2, columnspan=2)

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

def main():
    global w
    
    w = tk.Tk()
    w.title('Pytesseract interactive filtering')

    sp.call(['convert', infi, outfi])

    # pytesseract output
    tesseract = tk.Label(w, text='', name='tesseract', font='Helvetica 16').grid(row=0, columnspan=2)

    img = tk.PhotoImage(file=infi)
    l = tk.Label(w, image=img).grid(row=1, columnspan=2)

    img2 = tk.PhotoImage(file=outfi)
    l2 = tk.Label(w, image=img2, name='img_label').grid(row=2, columnspan=2)

    # ======== SCALES ========
    lab_sre = tk.Label(w, name='lab_sre', text='Resize').grid(row=3, column=0, sticky=tk.W)

    sre = tk.Scale(w, name='sre', orient=tk.HORIZONTAL, length=300, resolution=25, from_=100, to=1000, tickinterval=900, command=updateSize).grid(row=3, column=1)
    h = w.nametowidget('sre')
    h.set(200)


    lab_sth = tk.Label(w, name='lab_sth', text='Threshold').grid(row=4, column=0, sticky=tk.W)

    sth = tk.Scale(w, name='sth', orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=100, tickinterval=100, command=updateThreshold).grid(row=4, column=1)
    h = w.nametowidget('sth')
    h.set(85)


    lab_sbr = tk.Label(w, name='lab_sbr', text='Brightness').grid(row=5, column=0, sticky=tk.W)

    sbr = tk.Scale(w, name='sbr', orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=updateBrightness).grid(row=5, column=1)
    h = w.nametowidget('sbr')
    h.set(-42)


    lab_sco = tk.Label(w, name='lab_sco', text='Contrast').grid(row=6, column=0, sticky=tk.W)

    sco = tk.Scale(w, name='sco', orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=updateContrast).grid(row=6, column=1)
    h = w.nametowidget('sco')
    h.set(100)


    lab_sbo = tk.Label(w, name='lab_sbo', text='Border size').grid(row=7, column=0, sticky=tk.W)

    sbo = tk.Scale(w, name='sbo', orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=10, tickinterval=10, command=updateBorder).grid(row=7, column=1)
    h = w.nametowidget('sbo')
    h.set(3)

    # ====== /SCALES ======
    
    check_timings_btn = tk.Button(w, text='Check timings with following\n amount of iterations', name='check_timings_btn', command=check_timings).grid(row=8, column=0)

    num_of_iterations = tk.Text(w, name='num_of_iterations_text', width=4, height=1).grid(row=8, column=1, sticky=tk.W)
    h = w.nametowidget('num_of_iterations_text')
    h.insert(tk.END, str(NUM_OF_ITERATIONS))
    
    # time to execute pytesseract image_to_string, i.e. read the image
    lab_exec_pytess = tk.Label(w, name='lab_exec_pytess', text='Exec. time pytesseract [s]').grid(row=9, column=0, sticky=tk.W)
    exectime_pytess = tk.Label(w, text='', name='exectime_pytess', font='Helvetica 16').grid(row=9, column=1)

    # time to invoke the 'convert' function and execute it
    lab_exec_conv = tk.Label(w, name='lab_exec_conv', text='Exec. time convert [s]').grid(row=10, column=0, sticky=tk.W)
    exectime_convert = tk.Label(w, text='', name='exectime_convert', font='Helvetica 16').grid(row=10, column=1)
        
    w.mainloop()
    
if __name__ == '__main__':
    main()
