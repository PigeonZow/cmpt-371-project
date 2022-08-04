from tabnanny import check
from tkinter import *
import tkinter.font as font
import math
from turtle import clear

WINDOW = None

current_x, current_y = 0,0
color = 'black'
currentBox = (-1, -1) # col, row

class MainView(Frame):
    def __init__(self, *args, **kwargs):
        container = Frame()
        container.grid(row=0, column=0, sticky='nsew')
        self.listing = {}
        for p in (HomePage, GamePage):
            page_name = p.__name__
            frame = p(parent = container, controller = self)
            frame.grid(row=0, column=0, sticky='nsew')
            self.listing[page_name] = frame

        # self.listing['GamePage'].fillBox()
        self.up_frame('HomePage')

    def up_frame(self, page_name):
        page = self.listing[page_name]
        page.event_generate("<<ShowFrame>>")
        page.tkraise()

    def get_frame(self, page_name):
        page = self.listing[page_name]
        return page

class HomePage(Frame):
   def __init__(self, parent, controller):
       Frame.__init__(self, parent)
       self.controller = controller
       label = Label(self, text="Deny and Conquer", font=("Helvetica", 50))
       label.pack()
       buttonFont = font.Font(family='Helvetica', size=16, weight='bold')
       btn = Button(self, text = "Start", font=buttonFont, height=5, width=15, command= lambda: controller.up_frame('GamePage'))
       btn.pack()

class GamePage(Frame):

    def __init__(self, parent, controller):
        global WINDOW
        
        Frame.__init__(self, parent)

        canvas = Canvas(self, background='yellow', width=1200, height=900) 
        canvas.grid(row=0,column=0)
        WINDOW.update()
        boxAreas = [[0 for x in range(8)] for y in range(8)]
        col_width = canvas.winfo_width()/8
        row_height = canvas.winfo_height()/8
        self.mycanvas = canvas
        self.myColWidth = col_width
        self.myRowHeight = row_height

        def getBox(event):
            col_width = self.mycanvas.winfo_width()/8
            row_height = self.mycanvas.winfo_height()/8
            # Calculate column and row number
            col = int(event.x//col_width)
            row = int(event.y//row_height)
            return (col, row)

        def locate_xy(event):
            global current_x, current_y
            global currentBox
            current_x, current_y = event.x, event.y
            currentBox = getBox(event)

        def addLine(event):
            global current_x, current_y
            box = getBox(event)
            if box == currentBox and boxAreas[box[1]][box[0]] >= 0:
                c = color
                self.mycanvas.create_line((current_x,current_y,event.x,event.y),fill = c, width=5)
                fillArea(lineLength(current_x, current_y, event.x, event.y) * 5, box[0], box[1], event)
                current_x, current_y = event.x, event.y
                # Send packet temporarily locking box for player (This bombards the server every tick the player draws)

        def lineLength(x0,y0,x1,y1):
            xdiff = (x1 - x0)**2
            ydiff = (y1 - y0)**2
            return math.sqrt(xdiff+ydiff)

        def fillArea(linelen, col, row, event):
            boxAreas[row][col] += linelen
            if boxAreas[row][col]/(col_width*row_height) >= 0.5:
                boxAreas[row][col] = -1
                lockBox(event)

        def clearBox(event):
            box = getBox(event)
            c='white'
            if (0 <= box[0] <= 7) and (0 <= box[1] <= 7):
                if boxAreas[box[1]][box[0]] < 0:
                    c = 'grey'
                else:
                    boxAreas[box[1]][box[0]] = 0
                self.mycanvas.create_rectangle(box[0]*col_width, box[1]*row_height, (box[0]+1)*col_width, (box[1]+1)*row_height, fill=c)
            else:
                if boxAreas[currentBox[1]][currentBox[0]] < 0:
                    c = 'grey'
                else:
                    boxAreas[currentBox[1]][currentBox[0]] = 0
                self.mycanvas.create_rectangle(currentBox[0]*col_width, currentBox[1]*row_height, (currentBox[0]+1)*col_width, (currentBox[1]+1)*row_height, fill=c)

        def checkEndgame():
            gameEnd = True
            for i in range(8):
                for j in range(8):
                    if boxAreas[i][j] >= 0:
                        gameEnd = False
            # Server will probably handle end game
            if gameEnd:
                controller.up_frame('HomePage')

        def lockBox(event):
            box = getBox(event)
            self.mycanvas.create_rectangle(box[0]*col_width, box[1]*row_height, (box[0]+1)*col_width, (box[1]+1)*row_height, fill="grey")
            # Send packet to permanently lock ownership of this box to player
            checkEndgame()

        def makeBoxes(event):
            print('makeboxes')
            for i in range(8):
                for j in range(8):
                    boxAreas[i][j] = 0
                    self.mycanvas.create_rectangle(j*col_width, i*row_height, (j+1)*col_width, (i+1)*row_height, outline="black", fill="white")

        self.mycanvas.bind('<Button-1>', locate_xy)
        self.mycanvas.bind('<B1-Motion>',addLine)
        self.mycanvas.bind('<ButtonRelease-1>', clearBox)
        self.bind("<<ShowFrame>>", makeBoxes)

    def fillBox(self):
        print('fillbox')
        self.mycanvas.create_rectangle(1*self.myColWidth, 1*self.myRowHeight, (1+1)*self.myColWidth, (1+1)*self.myRowHeight, fill="red")
        # gui1.main.get_frame('GamePage').fillBox()

def startGUI():
    global WINDOW
    WINDOW = Tk()
    WINDOW.geometry("1200x900")
    WINDOW.rowconfigure(0, weight=1)
    WINDOW.columnconfigure(0, weight=1)
    WINDOW.resizable(False,False)
    main = MainView(WINDOW)
    # main.pack(side="top", fill="both", expand=True)

    WINDOW.mainloop()