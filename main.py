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

class Controls(tk.Frame):
        theOtherWindow  = None        
        master          = None
        
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
        
        img1 = None
        
        def __init__(self, master=None):
            super().__init__(master)
            
            self.master = master
            
            # I need to figure out widthxheight in order to use '-rotate'. See https://imagemagick.org/script/command-line-options.php#rotate
            global infi            
            im = Image.open(infi)
            width, height = im.size
            if width > height:
                self.rotationdir = '>'
            else:
                self.rotationdir = '<'
            
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
            saveCurrent = tk.Button(master, text='Save current configuration', command=self.saveCurrent).grid(row=row, column=0)
            loadLast    = tk.Button(master, text='Load last configuration', command=self.loadLast).grid(row=row, column=1)
            
            row += 1
            generateCommand = tk.Button(master, text='Generate command', command=self.generateCommand).grid(row=row, column=0)
            commandOutput   = tk.Text(master, wrap=tk.WORD, name='commandOutput', height=3, width=50, font='Helvetica 8').grid(row=row, column=1)
            
            row += 1
            check_timings_btn = tk.Button(master, text='Check timings with following\n amount of iterations', name='check_timings_btn', command=self.check_timings).grid(row=row, column=0)
            num_of_iterations = tk.Text(master, name='num_of_iterations_text', width=6, height=1).grid(row=row, column=1)
            h = master.nametowidget('num_of_iterations_text')
            h.insert(tk.END, str(self.NUM_OF_ITERATIONS))
            
            row += 1
            # time to execute pytesseract image_to_string, i.e. read the image
            lab_exec_pytess = tk.Label(master, name='lab_exec_pytess', text='Exec. time pytesseract [s]').grid(row=row, column=0, sticky=tk.W)
            exectime_pytess = tk.Label(master, text='', name='exectime_pytess', font='Helvetica 16').grid(row=row, column=1)
            
            row += 1
            # time to invoke the 'convert' function and execute it
            lab_exec_conv       = tk.Label(master, name='lab_exec_conv', text='Exec. time convert [s]').grid(row=row, column=0, sticky=tk.W)
            exectime_convert    = tk.Label(master, text='', name='exectime_convert', font='Helvetica 16').grid(row=row, column=1)
        
        # === MOUSE STUFF ===
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
                self.theOtherWindow.lower()
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
            # TODO: make pressing "esc" stop the acquisition, without replacing the image. need to bind a command to that key. see pynput
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
                
                self.completeImageAcquisition(self.startXY, self.endXY) # scrot take pic
                self.setNewOriginalImage()
                self.updateImage()
            else:
                print('why am I here? shouldnt be reachable')
        
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
            
            width = abs(width)
            height = abs(height)
            
            sp.call(['scrot',infi])
            sp.call(['convert', infi, '-crop', str(width)+'x'+str(height)+'+'+str(x)+'+'+str(y), infi])
            
        def setNewOriginalImage(self):
            # redraw update image
            # destroy old
            h = self.theOtherWindow.nametowidget('original_img_label')
            h.destroy()
            
            #create new
            global updating_image_row
            global infi
            self.img1 = tk.PhotoImage(file=infi)
            l = tk.Label(self.theOtherWindow, image=self.img1, name='original_img_label').grid(row=updating_image_row-1)
            
        # === /MOUSE STUFF ===
        
        def generateCommand(self):
            h = self.master.nametowidget('commandOutput')
            h.delete('1.0', tk.END)
            h.insert(tk.END, ' '.join(self.last_command))
        
        def saveCurrent(self):
            self.current_state = [self.size, self.threshold, self.brightness, self.contrast, self.border, self.rotation]
        
        def loadLast(self):
            h = self.master.nametowidget('sre')
            h.set(self.current_state[0])
            h = self.master.nametowidget('sth')
            h.set(self.current_state[1])
            h = self.master.nametowidget('sbr')
            h.set(self.current_state[2])
            h = self.master.nametowidget('sco')
            h.set(self.current_state[3])
            h = self.master.nametowidget('sbo')
            h.set(self.current_state[4])
            h = self.master.nametowidget('sro')
            h.set(self.current_state[5])
            
            self.updateImage()
            
        def setTheOtherWindow(self, tow):
            self.theOtherWindow = tow
        
        def updateRotation(self, value):
            self.rotation = value
            self.updateImage()
        
        def updateThreshold(self, value):
            self.threshold = value
            self.updateImage()
            
        def updateSize(self, value):
            self.size = value
            self.updateImage()
            
        def updateContrast(self, value):
            self.contrast = value
            self.updateImage()

        def updateBrightness(self, value):
            self.brightness = value
            self.updateImage()

        def updateBorder(self, value):
            self.border = value
            self.updateImage()
            
        def updateImage(self):
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
                        
            read = pytesseract.image_to_string(Image.open(outfi), lang='eng')           
            
            h = self.theOtherWindow.nametowidget('tesseract')
            h.config(text=read)
            
            # redraw update image
            # destroy old
            h = self.theOtherWindow.nametowidget('img_label')
            h.destroy()
            
            #create new
            global updating_image_row
            self.img2 = tk.PhotoImage(file=outfi)
            l = tk.Label(self.theOtherWindow, image=self.img2, name='img_label').grid(row=updating_image_row)
            
        def check_timings(self):
            h = self.master.nametowidget('num_of_iterations_text')
            self.NUM_OF_ITERATIONS = int(h.get('current linestart', tk.END))

            avg_convert     = 0
            avg_tesseract   = 0
            global outfi
            for i in range(self.NUM_OF_ITERATIONS):
                s = time.time()
                sp.call(self.last_command)
                
                s1 = time.time()
                
                read = pytesseract.image_to_string(Image.open(outfi))
                s2 = time.time()
                
                avg_convert     += s1-s
                avg_tesseract   += s2-s1

            avg_convert     /= self.NUM_OF_ITERATIONS
            avg_tesseract   /= self.NUM_OF_ITERATIONS

            h = self.master.nametowidget('exectime_convert')
            h.config(text=str(avg_convert))

            h = self.master.nametowidget('exectime_pytess')
            h.config(text=str(avg_tesseract))
        
class Display(tk.Frame):
        img = ''
        img2 = ''
        master = None
        
        def __init__(self, master=None):
            super().__init__(master)
            
            self.master = master
            
            row = 0
            
            # pytesseract output
            tesseract = tk.Label(master, text='', name='tesseract', font='Helvetica 16').grid(row=row)
            
            global infi
            global outfi
            row += 1
            self.img = tk.PhotoImage(file=infi)
            l = tk.Label(master, name='original_img_label', image=self.img).grid(row=row)
            
            row += 1
            global updating_image_row
            updating_image_row = row
            self.img2 = tk.PhotoImage(file=outfi)
            l2 = tk.Label(master, image=self.img2, name='img_label').grid(row=row)
    
def main():    
    # just to create an output file immediately
    # TODO: check if image exists and non 'empty'
    global infi
    global outfi
    sp.call(['convert', infi, outfi])
    
    root = tk.Tk()
    root.title('Controls - Ocr pytesseract interactive image processing')
    controls = Controls(root)
    
    # get screen width and height
    #ws = root.winfo_screenwidth() # width of the screen
    #hs = root.winfo_screenheight() # height of the screen
    root.geometry('+150+150')

    second_win = tk.Toplevel(root)
    second_win.title('Display - Ocr pytesseract interactive image processing')
    second_win.geometry('+750+150')
    d = Display(second_win)
    
    controls.setTheOtherWindow(second_win)
    
    root.mainloop()
    
if __name__ == '__main__':
    main()
