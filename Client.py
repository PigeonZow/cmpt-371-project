import socket
import argparse
import threading

from tabnanny import check
from tkinter import *
import tkinter.font as font
import math
from turtle import clear

# Defaults
SERVER_IP = socket.gethostname()
PORT = 9999
BUFFER = 128
SOCKET = None

COLOR = None
LISTENING = True

GAME_WINDOW = None

def fillerFunc():
    print("blah")

def startListener(s):
    global LISTENING
    global GAME_WINDOW

    while LISTENING:
        receive = s.recv(BUFFER).decode('utf-8')
        arg = receive.split(' ')

        if (arg[0] == "DISCONNECT" or arg[0] == "STOP"):
            # Stop listener thread
            print("Press enter again to stop...")
            LISTENING = False
            break

        elif (arg[0] == "LOCK"):
            # Server tells client that square at (x,y) is locked
            # LOCK x y
            x = arg[1]
            y = arg[2]
            player_num = int(arg[3])
            # ...code here for client to lock square at (x,y)
            # ...call functions in Client_GUI.py to manipulate GUI
            print(f"lock box {x} {y} for {player_num}")
            GAME_WINDOW.fillBox(x, y, player_num)

        elif (arg[0] == "UNLOCK"):
            # Server tells client that square at (x,y) is unlocked
            # UNLOCK x y
            x = arg[1]
            y = arg[2]
            # ...code here for client to unlock square at (x,y)
            # ...call functions in Client_GUI.py to manipulate GUI

        elif (arg[0] == "CLAIM"):
            # Server tells client that square at (x,y) is claimed by (color)
            # CLAIM x y color
            x = arg[1]
            y = arg[2]
            color = arg[3]
            # ...code here for client to lock square at (x,y) and color it
            # ...call functions in Client_GUI.py to manipulate GUI

        elif (arg[0] == "START"):
            # Server tells client that game has started
            fillerFunc()
            # ...call functions in Client_GUI.py to manipulate GUI

        elif (arg[0] == "RESTART"):
            # Server tells client to restart game (reset GUI)
            fillerFunc()
            # ...call functions in Client_GUI.py to manipulate GUI

        elif (arg[0] == "END"):
            # Server tells client that game has ended and which color won the game
            # END color
            color = arg[1]
            # ...call functions in Client_GUI.py to manipulate GUI

        else:
            print(receive)

    s.close()


def startInput(s):
    global LISTENING

    while LISTENING:
        msg = input()
        if (LISTENING):
            s.send(msg.encode('utf-8'))


def connect(ip, port):
    global MY_PLAYER_NUMBER
    global SOCKET

    # Create a socket
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect socket to the server
    SOCKET.connect((ip, port))
    print(f"[CONNECTED] to {ip}")

    #Store player's number
    MY_PLAYER_NUMBER = int(SOCKET.recv(BUFFER).decode('utf-8'))
    print(MY_PLAYER_NUMBER)

    # Run separate threads for listening to server payloads, and receiving input from user (for testing)
    threading.Thread(target=startListener, args=(SOCKET,)).start()
    threading.Thread(target=startInput, args=(SOCKET,)).start()

WINDOW = None

my_current_x, my_current_y = 0,0

currentPos = [(0,0), (0,0), (0,0), (0,0), (0,0)]
color = ["black", "red", "blue", "green", "yellow"]
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
        global SOCKET

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
            global my_current_x, my_current_y
            global currentBox
            my_current_x, my_current_y = event.x, event.y
            currentBox = getBox(event)

        def addLine(event):
            global my_current_x, my_current_y
            box = getBox(event)
            if box == currentBox and boxAreas[box[1]][box[0]] >= 0:
                c = color[MY_PLAYER_NUMBER]
                self.mycanvas.create_line((my_current_x,my_current_y,event.x,event.y),fill = c, width=5)
                fillArea(lineLength(my_current_x, my_current_y, event.x, event.y) * 5, box[0], box[1], event)
                my_current_x, my_current_y = event.x, event.y
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
                    c = color[MY_PLAYER_NUMBER]
                else:
                    boxAreas[box[1]][box[0]] = 0
                self.mycanvas.create_rectangle(box[0]*col_width, box[1]*row_height, (box[0]+1)*col_width, (box[1]+1)*row_height, fill=c)
            else:
                if boxAreas[currentBox[1]][currentBox[0]] < 0:
                    c = color[MY_PLAYER_NUMBER]
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
            msg = f'LOCK {box[0]} {box[1]} {MY_PLAYER_NUMBER}'
            SOCKET.send(msg.encode('utf-8'))
            print("sending lock request")
            checkEndgame()

        def makeBoxes(event):
            print('makeboxes')
            for i in range(8):
                for j in range(8):
                    boxAreas[i][j] = 0
                    self.mycanvas.create_rectangle(j*col_width, i*row_height, (j+1)*col_width, (i+1)*row_height, outline="black", fill="white")

        self.mycanvas.bind('<Button-1>', locate_xy)
        self.mycanvas.bind('<B1-Motion>', addLine)
        self.mycanvas.bind('<ButtonRelease-1>', clearBox)
        self.bind("<<ShowFrame>>", makeBoxes)

    def fillBox(self, x, y, player_num):
        x = int(x)
        y = int(y)
        print(f'fill box {x} {y} {player_num}')
        self.mycanvas.create_rectangle(x*self.myColWidth, y*self.myRowHeight, (x+1)*self.myColWidth, (y+1)*self.myRowHeight, fill=str(color[player_num]).lower())
        # gui1.main.get_frame('GamePage').fillBox()

def startGUI():
    global WINDOW
    global GAME_WINDOW
    WINDOW = Tk()
    WINDOW.geometry("1200x900")
    WINDOW.rowconfigure(0, weight=1)
    WINDOW.columnconfigure(0, weight=1)
    WINDOW.resizable(False,False)
    main = MainView(WINDOW)
    GAME_WINDOW = main.get_frame("GamePage")
    # main.pack(side="top", fill="both", expand=True)

    WINDOW.mainloop()

def main():
    global SERVER_IP
    global PORT

    # Parse arguments
    # (usage example: Client.py --ip 192.168.0.1 --port 9999)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=SERVER_IP)
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()

    SERVER_IP = args.ip
    PORT = args.port

    connect(args.ip, args.port)

    # Start GUI
    startGUI()

if __name__ == "__main__":
    main()
