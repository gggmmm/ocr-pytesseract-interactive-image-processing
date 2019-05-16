import tkinter as tk
import subprocess as sp
import time
from PIL import Image, ImageTk
import pytesseract

from pynput             import mouse, keyboard
from pynput.mouse       import Button
from pynput.keyboard    import Key

input_dir   = './'
input_file  = 'test.png'
infi        = input_dir+input_file
output_dir  = './'
output_file = 'test_output.png'
outfi       = output_dir+output_file
updating_image_row = 2

class Backend():
    size                = 100
    threshold           = 50
    brightness          = 0
    contrast            = 0
    border              = 3
    bordercolor         = 'White'
    rotation            = 0
    rotationdir         = '' # this value is fixed once and remains the same, I always use the original image as input
    
    current_state       = [100, 50, 0, 0, 3, 0] # size, threshold, brightness, contrast, border, rotation
    
    NUM_OF_ITERATIONS   = 10
    last_command        = []
    last_read           = ''
    
    def __init__(self):
        # I need to figure out widthxheight in order to use '-rotate'. See https://imagemagick.org/script/command-line-options.php#rotate
        global infi
        
        # TODO: check if image exists and non 'empty'
        im = Image.open(infi)
        width, height = im.size
        
        if width > height:
            self.rotationdir = '>'
        else:
            self.rotationdir = '<'
        
        # just to create an output file immediately
        global outfi
        sp.call(['convert', infi, outfi])

    def completeImageAcquisition(self, startXY, endXY):
        global infi
        
        xstart  = startXY[0]
        xend    = endXY[0]
        ystart  = startXY[1]
        yend    = endXY[1]
        
        width   = xend - xstart
        height  = yend - ystart
        
        x,y = [0]*2
        
        if width<0 and height<0: # going NW
            x,y = xend, yend
        elif width>0 and height>0: # going SE
            x,y = xstart, ystart
        elif width<0 and height>0: # going SW
            x,y = xend, ystart
        elif width>0 and height<0: # going NE
            x,y = xstart, yend
        
        width   = abs(width)
        height  = abs(height)
        
        sp.call(['scrot',infi])
        sp.call(['convert', infi, '-crop', str(width)+'x'+str(height)+'+'+str(x)+'+'+str(y), infi])
        
    def saveCurrentState(self):
        self.current_state = [self.size, self.threshold, self.brightness, self.contrast, self.border, self.rotation]
    
    def loadLastState(self):
        return self.current_state

    def updateRotation(self, value):
        self.rotation = value
        self.processImage()
    
    def updateThreshold(self, value):
        self.threshold = value
        self.processImage()
        
    def updateSize(self, value):
        self.size = value
        self.processImage()
        
    def updateContrast(self, value):
        self.contrast = value
        self.processImage()

    def updateBrightness(self, value):
        self.brightness = value
        self.processImage()

    def updateBorder(self, value):
        self.border = value
        self.processImage()
        
    def processImage(self):
        global infi
        global outfi
        
        self.last_command = [   'convert', infi, \
                                '-rotate', str(self.rotation)+self.rotationdir, \
                                '-resize', str(self.size)+'%', \
                                '-brightness-contrast', str(self.brightness)+'x'+str(self.contrast), \
                                '-threshold', str(self.threshold)+'%', \
                                '-border',str(self.border)+'x'+str(self.border), \
                                '-bordercolor', self.bordercolor, outfi]

        sp.call(self.last_command)
        
        self.last_read = pytesseract.image_to_string(Image.open(outfi), lang='eng')
        
    def check_timings(self, number_of_iterations):
        avg_convert     = 0
        avg_tesseract   = 0

        global outfi
        for i in range(number_of_iterations):
            s = time.time()
            sp.call(self.last_command)
            
            s1 = time.time()
            
            read = pytesseract.image_to_string(Image.open(outfi))
            s2 = time.time()
            
            avg_convert     += s1-s
            avg_tesseract   += s2-s1

        try:
            avg_convert     /= number_of_iterations
            avg_tesseract   /= number_of_iterations
        except e:
            print(e)

        return avg_convert, avg_tesseract
        
class WindowControls(tk.Frame):
    displayWindow  = None        
    master          = None
    backend         = None

    def __init__(self, master, backend):
        super().__init__(master)
        
        self.master         = master
        self.backend        = backend

        second_win = tk.Toplevel(master)
        second_win.title('Display - Ocr pytesseract interactive image processing')
        second_win.geometry('+750+150')
        self.displayWindow = WindowDisplay(second_win)

        # Creating GUI
        # ======== SCALES+LABELS ========
        row = 0
        
        selectImageFromScreen = tk.Button(master, name='selectImageFromScreenBtn', text='Select image from screen', command=self.selectImageFromScreen).grid(row=row, column=0)
        
        row += 1
        lab_sre = tk.Label(master, name='lab_sre', text='Resize').grid(row=row, column=0, sticky=tk.W)

        sre = tk.Scale(master, name='sre', orient=tk.HORIZONTAL, length=300, resolution=25, from_=100, to=1000, tickinterval=900, command=self.updateSize).grid(row=row, column=1)
        h = master.nametowidget('sre')
        h.set(100)


        row += 1
        lab_sth = tk.Label(master, name='lab_sth', text='Threshold').grid(row=row, column=0, sticky=tk.W)

        sth = tk.Scale(master, name='sth', orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=100, tickinterval=100, command=self.updateThreshold).grid(row=row, column=1)
        h = master.nametowidget('sth')
        h.set(85)


        row += 1
        lab_sbr = tk.Label(master, name='lab_sbr', text='Brightness').grid(row=row, column=0, sticky=tk.W)

        sbr = tk.Scale(master, name='sbr', orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=self.updateBrightness).grid(row=row, column=1)
        h = master.nametowidget('sbr')
        h.set(-42)


        row += 1
        lab_sco = tk.Label(master, name='lab_sco', text='Contrast').grid(row=row, column=0, sticky=tk.W)

        sco = tk.Scale(master, name='sco', orient=tk.HORIZONTAL, length=300, resolution=1, from_=-100, to=100, tickinterval=100, command=self.updateContrast).grid(row=row, column=1)
        h = master.nametowidget('sco')
        h.set(100)

        row += 1
        lab_sbo = tk.Label(master, name='lab_sbo', text='Border size').grid(row=row, column=0, sticky=tk.W)

        sbo = tk.Scale(master, name='sbo', orient=tk.HORIZONTAL, length=300, resolution=1, from_=0, to=10, tickinterval=10, command=self.updateBorder).grid(row=row, column=1)
        h = master.nametowidget('sbo')
        h.set(3)
        
        row += 1
        lab_rot = tk.Label(master, name='lab_rot', text='Rotation').grid(row=row, column=0, sticky=tk.W)

        sro = tk.Scale(master, name='sro', orient=tk.HORIZONTAL, length=300, resolution=1, from_=-180, to=180, tickinterval=90, command=self.updateRotation).grid(row=row, column=1)
        h = master.nametowidget('sro')
        h.set(0)

        # ====== /SCALES ======
        
        # ====== BUTTONS+TEXT =======
        row += 1
        saveCurrent = tk.Button(master, text='Save current configuration', command=self.saveCurrentState).grid(row=row, column=0)
        loadLast    = tk.Button(master, text='Load last configuration', command=self.loadLastState).grid(row=row, column=1)
        
        row += 1
        generateCommand = tk.Button(master, text='Generate command', command=self.generateCommand).grid(row=row, column=0)
        commandOutput   = tk.Text(master, wrap=tk.WORD, name='commandOutput', height=3, width=50, font='Helvetica 8').grid(row=row, column=1)
        
        row += 1
        check_timings_btn = tk.Button(master, text='Check timings with following\n amount of iterations', name='check_timings_btn', command=self.check_timings).grid(row=row, column=0)
        num_of_iterations = tk.Text(master, name='num_of_iterations_text', width=6, height=1).grid(row=row, column=1)
        h = master.nametowidget('num_of_iterations_text')
        h.insert(tk.END, '10')
        
        row += 1
        # time to execute pytesseract image_to_string, i.e. read the image
        lab_exec_pytess = tk.Label(master, name='lab_exec_pytess', text='Exec. time pytesseract [s]').grid(row=row, column=0, sticky=tk.W)
        exectime_pytess = tk.Label(master, text='', name='exectime_pytess', font='Helvetica 16').grid(row=row, column=1)
        
        row += 1
        # time to invoke the 'convert' function and execute it
        lab_exec_conv       = tk.Label(master, name='lab_exec_conv', text='Exec. time convert [s]').grid(row=row, column=0, sticky=tk.W)
        exectime_convert    = tk.Label(master, text='', name='exectime_convert', font='Helvetica 16').grid(row=row, column=1)

    def updateImage(self):
        global outfi
        self.displayWindow.setProcessedImage(outfi)
        self.setPytesseractText()

    def updateRotation(self, value):
        self.backend.updateRotation(value)
        self.updateImage()
    
    def updateThreshold(self, value):
        self.backend.updateThreshold(value)
        self.updateImage()
        
    def updateSize(self, value):
        self.backend.updateSize(value)
        self.updateImage()
        
    def updateContrast(self, value):
        self.backend.updateContrast(value)
        self.updateImage()

    def updateBrightness(self, value):
        self.backend.updateBrightness(value)
        self.updateImage()

    def updateBorder(self, value):
        self.backend.updateBorder(value)
        self.updateImage()

    def setNewOriginalImage(self):
            global infi
            self.displayWindow.setOriginalImage(infi)

    def generateCommand(self):
        h   = self.master.nametowidget('commandOutput')
        
        h.delete('1.0', tk.END)
        h.insert(tk.END, ' '.join( self.backend.last_command ))

    def setPytesseractText(self):
        self.displayWindow.updateTesseractLabel(self.backend.last_read)

    # === MOUSE/KEYBOARD STUFF ===

    mouseListener = None
    keyboardListener = None
    transparentLayer = None
    def selectImageFromScreen(self):
        if self.mouseListener==None and self.keyboardListener==None:
            self.mouseListener = mouse.Listener(on_click=self.on_click)
            self.mouseListener.start()
            
            self.keyboardListener = keyboard.Listener(on_press=self.on_press)
            self.keyboardListener.start()
            
            # make window disappear
            self.displayWindow.lower()
            self.master.lower()
            
            #create transparent layer-window on top
            
            ws = self.master.winfo_screenwidth() # width of the screen
            hs = self.master.winfo_screenheight() # height of the screen

            second_win = tk.Toplevel(self.master, bg='red', cursor='sizing')
            second_win.geometry(str(ws)+'x'+str(hs))
            
            second_win.wait_visibility(second_win)
            second_win.wm_attributes('-alpha',0.1)
            
            self.transparentLayer = second_win
    
    def on_press(self, key):
        if Key.esc==key:
            self.mouseListener.stop()
            self.keyboardListener.stop()
            self.transparentLayer.destroy()
            
            self.mouseListener = None
            self.keyboardListener = None
            self.transparentLayer = None
            
            self.mouseState = 0
            self.startXY    = (0,0)
            self.endXY      = (0,0)
    
    mouseState  = 0
    startXY     = (0,0)
    endXY       = (0,0)
    def on_click(self, x, y, button, pressed):
        # TODO: (?) check selected area, if too small just ignore it (10px*10px??)
        # TODO: make appear dialog box "want to use this image?" so to avoid the problem all together
        if self.mouseState==0 and pressed and button==Button.left:
            self.startXY = (x,y)
            self.mouseState = 1
        elif self.mouseState==1 and not pressed and button==Button.left:
            self.mouseListener.stop()
            self.mouseListener = None
            
            self.keyboardListener.stop()
            self.keyboardListener = None
            
            self.endXY = (x,y)
            self.mouseState = 0
            
            self.transparentLayer.destroy()
            time.sleep(0.15) # a little wait or the red layer is caught
            
            self.backend.completeImageAcquisition(self.startXY, self.endXY) # scrot take pic
            self.setNewOriginalImage()
            self.backend.processImage()
            self.updateImage()  
            self.setPytesseractText()
        else:
            print('why am I here? shouldnt be reachable')

    # === END MOUSE/KEYBOARD STUFF ===

    def check_timings(self):
        h = self.master.nametowidget('num_of_iterations_text')
        number_of_iterations = int(h.get('current linestart', tk.END))

        avg_convert, avg_tesseract = self.backend.check_timings(number_of_iterations)

        h = self.master.nametowidget('exectime_convert')
        h.config(text=str(avg_convert))

        h = self.master.nametowidget('exectime_pytess')
        h.config(text=str(avg_tesseract))

    def loadLastState(self):
        current_state = self.backend.loadLastState()

        h = self.master.nametowidget('sre')
        h.set(current_state[0])
        h = self.master.nametowidget('sth')
        h.set(current_state[1])
        h = self.master.nametowidget('sbr')
        h.set(current_state[2])
        h = self.master.nametowidget('sco')
        h.set(current_state[3])
        h = self.master.nametowidget('sbo')
        h.set(current_state[4])
        h = self.master.nametowidget('sro')
        h.set(current_state[5])

    def saveCurrentState(self):
        self.backend.saveCurrentState()
        
class WindowDisplay(tk.Frame):
    imgOrig             = None
    imgProc             = None
    labelOriginalImage  = None
    labelProcessedImage = None
    labelTesseract      = None

    master              = None

    def __init__(self, master):
        super().__init__(master)
        
        global infi
        global outfi
        self.master = master
        
        # pytesseract output
        self.labelTesseract = tk.Label(master, font='Helvetica 16', name='py_tesseract_label').grid(row=0)

        self.imgOrig = tk.PhotoImage(file=infi)
        self.labelOriginalImage = tk.Label(self.master, image=self.imgOrig, name='img_orig').grid(row=1)

        self.imgProc = tk.PhotoImage(file=outfi)
        self.labelProcessedImage = tk.Label(self.master, image=self.imgProc, name='img_proc').grid(row=2)

    def updateTesseractLabel(self, text):
        h = self.master.nametowidget('py_tesseract_label')
        h.config(text=text)

    def setOriginalImage(self, fileName):
        h = self.master.nametowidget('img_orig')
        h.destroy()

        self.imgOrig = tk.PhotoImage(file=fileName)
        self.labelOriginalImage = tk.Label(self.master, image=self.imgOrig, name='img_orig').grid(row=1)

    def setProcessedImage(self, fileName):
        h = self.master.nametowidget('img_proc')
        h.destroy()

        self.imgProc = tk.PhotoImage(file=fileName)
        self.labelProcessedImage = tk.Label(self.master, image=self.imgProc, name='img_proc').grid(row=2)

def main():
    master = tk.Tk()

    backend = Backend()
    
    master.title('Controls - Ocr pytesseract interactive image processing')
    master.geometry('+150+150')
    controls = WindowControls(master, backend)

    master.mainloop()
    
if __name__ == '__main__':
    main()
