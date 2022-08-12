import socket
import argparse
import threading
import pickle

from tkinter import *
import tkinter.font as font
import math

# Defaults
SERVER_IP = socket.gethostname()
PORT = 9999
BUFFER = 1024
SOCKET = None

COLOR = None
LISTENING = True

GAME_WINDOW = None
END_WINDOW = None


def fillerFunc():
    print("blah")


def startListener(s):
    global LISTENING
    global GAME_WINDOW
    global END_WINDOW

    while LISTENING:
        receiveUtf = True
        receiveData = s.recv(BUFFER)
        try:
            receive = receiveData.decode('utf-8')
        except:
            receiveUtf = False
            claimedArr = pickle.loads(receiveData)
            arrLen = len(claimedArr)
            for i in range(arrLen):
                GAME_WINDOW.fillBox(claimedArr[i][0], claimedArr[i][1], claimedArr[i][2])

        if (receiveUtf):
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
                color = arg[3]
                # ...code here for client to lock square at (x,y)
                # ...call functions in Client_GUI.py to manipulate GUI
                if color != COLOR:
                    GAME_WINDOW.lockPlayersBox(x, y, color)
            elif (arg[0] == "UNLOCK"):
                # Server tells client that square at (x,y) is unlocked
                # UNLOCK x y
                x = arg[1]
                y = arg[2]
                color = arg[3]
                # ...code here for client to unlock square at (x,y)
                # ...call functions in Client_GUI.py to manipulate GUI
                if color != COLOR:
                    GAME_WINDOW.unlockPlayersBox(x, y)
            elif (arg[0] == "CLAIM"):
                # Server tells client that square at (x,y) is claimed by (color)
                # CLAIM x y color
                x = arg[1]
                y = arg[2]
                color = arg[3]
                GAME_WINDOW.fillBox(x, y, color)
                # ...code here for client to lock square at (x,y) and color it
                # ...call functions in Client_GUI.py to manipulate GUI
            elif (arg[0] == "START"):
                # Server tells client that game has started
                claimedStr = arg[1]
                print(claimedStr)
                claimedArr = pickle.loads(claimedStr.encode('utf-8'))
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
                claimedArr = pickle.loads(receiveData)
                print(claimedArr)
        receive = s.recv(BUFFER).decode('utf-8')
        print("recieve msg: ", receive)
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
            color = arg[3]
            # ...code here for client to lock square at (x,y)
            # ...call functions in Client_GUI.py to manipulate GUI
            if color != COLOR:
                GAME_WINDOW.lockPlayersBox(x, y, color)
        elif (arg[0] == "UNLOCK"):
            # Server tells client that square at (x,y) is unlocked
            # UNLOCK x y
            x = arg[1]
            y = arg[2]
            color = arg[3]
            # ...code here for client to unlock square at (x,y)
            # ...call functions in Client_GUI.py to manipulate GUI
            if color != COLOR:
                GAME_WINDOW.unlockPlayersBox(x, y)
        elif (arg[0] == "CLAIM"):
            # Server tells client that square at (x,y) is claimed by (color)
            # CLAIM x y color
            x = arg[1]
            y = arg[2]
            color = arg[3]
            GAME_WINDOW.fillBox(x, y, color)
            # ...code here for client to lock square at (x,y) and color it
            # ...call functions in Client_GUI.py to manipulate GUI
        elif (arg[0] == "START"):
            # Server tells client that game has started
            claimedStr = arg[1]
            claimedArr = pickle.loads(claimedStr.encode('utf-8'))
            print(claimedArr)
            # ...call functions in Client_GUI.py to manipulate GUI
        elif (arg[0] == "RESTART"):
            # Server tells client to restart game (reset GUI)
            fillerFunc()
            # ...call functions in Client_GUI.py to manipulate GUI
        elif (arg[0] == "ENDPAGE"):
            END_WINDOW.winUpdate(arg[1])
            if color != COLOR:
                GAME_WINDOW.bringUpEnd()
        elif (arg[0] == "END"):
            # Server tells client that game has ended and which color won the game
            # END color
            print(f"[DISCONNECTED] Winner: {arg[1]}. Press any key to exit program.")
            LISTENING = False
            break
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
    global COLOR
    global SOCKET

    # Create a socket
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect socket to the server
    SOCKET.connect((ip, port))
    print(f"[CONNECTED] to {ip}")

    # Store assigned color on client side
    COLOR = SOCKET.recv(BUFFER).decode('utf-8')
    print(COLOR)

    # Run separate threads for listening to server payloads, and receiving input from user (for testing)
    threading.Thread(target=startListener, args=(SOCKET,)).start()
    threading.Thread(target=startInput, args=(SOCKET,)).start()


WINDOW = None

current_x, current_y = 0, 0
currentBox = (-1, -1)  # col, row
lockedBoxes = [[0 for x in range(8)] for y in range(8)]
boxAreas = [[0 for x in range(8)] for y in range(8)]


class MainView(Frame):
    def __init__(self, *args, **kwargs):
        container = Frame()
        container.grid(row=0, column=0, sticky='nsew')
        self.listing = {}
        for p in (HomePage, GamePage, EndPage):
            page_name = p.__name__
            frame = p(parent=container, controller=self)
            frame.grid(row=0, column=0, sticky='nsew')
            self.listing[page_name] = frame

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
        btn = Button(self, text = "Start", font=buttonFont, height=5, width=15, command= lambda: self.startGame())
        btn.pack()

    def startGame(self):
        self.controller.up_frame('GamePage')
        connect(SERVER_IP, PORT)
        btn = Button(self, text="Start", font=buttonFont, height=5,
                     width=15, command=lambda: controller.up_frame('GamePage'))
        def connectToServer(event=None):
            global SERVER_IP
            global PORT
            connect(SERVER_IP, PORT)
        btn.bind('<Button-1>', connectToServer)
        btn.pack()

class EndPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="Game Over", font=("Helvetica", 50))
        label.pack()
        buttonFont = font.Font(family='Helvetica', size=16, weight='bold')
        btn = Button(self, text = "Disconnect", font=buttonFont, height=5, width=15, command=lambda: end())
        btn.pack()

        def end():
            SOCKET.send("END".encode('utf-8'))
            WINDOW.destroy()

    def winUpdate(self, arg):
        label2txt = "Player won: " + arg
        label2 = Label(self, text=label2txt, font=("Helvetica", 40), fg=str(arg).lower())
        label2.pack()


class GamePage(Frame):

    def __init__(self, parent, controller):
        global WINDOW
        global SOCKET
        global CONTROL2
        CONTROL2 = controller

        Frame.__init__(self, parent)

        canvas = Canvas(self, background='yellow', width=1200, height=900)
        canvas.grid(row=0, column=0)
        WINDOW.update()
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
            if boxAreas[currentBox[1]][currentBox[0]] >= 0 and lockedBoxes[currentBox[1]][currentBox[0]] == 0:
                lockBox(currentBox[0], currentBox[1])

        def addLine(event):
            global current_x, current_y
            box = getBox(event)
            if box == currentBox and boxAreas[box[1]][box[0]] >= 0 and lockedBoxes[currentBox[1]][currentBox[0]] == 0:
                c = COLOR
                self.mycanvas.create_line(
                    (current_x, current_y, event.x, event.y), fill=c, width=5)
                fillArea(lineLength(current_x, current_y,
                         event.x, event.y) * 5, box[0], box[1])
                current_x, current_y = event.x, event.y

        def lineLength(x0, y0, x1, y1):
            xdiff = (x1 - x0)**2
            ydiff = (y1 - y0)**2
            return math.sqrt(xdiff+ydiff)

        def fillArea(linelen, col, row):
            boxAreas[row][col] += linelen
            if boxAreas[row][col]/(col_width*row_height) >= 0.5:
                boxAreas[row][col] = -1
                claimBox(col, row)

        def clearBox(event):
            if boxAreas[currentBox[1]][currentBox[0]] >= 0 and lockedBoxes[currentBox[1]][currentBox[0]] == 0:
                boxAreas[currentBox[1]][currentBox[0]] = 0
                unlockBox(currentBox[0], currentBox[1])
                self.mycanvas.create_rectangle(currentBox[0]*col_width, currentBox[1]*row_height, (
                    currentBox[0]+1)*col_width, (currentBox[1]+1)*row_height, fill='white')

        def lockBox(col, row):
            # Send packet to temporarily lock ownership of this box to player
            msg = f'LOCK {col} {row} {COLOR}'
            SOCKET.send(msg.encode('utf-8'))

        def unlockBox(col, row):
            #Tell other players that this box is unlocked
            # box = getBox(event)
            #locked_boxAreas[box[0]][box[1]] = 0
            # Tell other players that this box is unlocked
            msg = f'UNLOCK {col} {row} {COLOR}'
            SOCKET.send(msg.encode('utf-8'))

        def claimBox(col, row):
            msg = f'CLAIM {col} {row} {COLOR}'
            SOCKET.send(msg.encode('utf-8'))
            checkEndgame()

        def checkEndgame():
            gameEnd = True
            for i in range(8):
                for j in range(8):
                    if boxAreas[i][j] >= 0:
                        gameEnd = False
            # Send end state to Server
            if gameEnd:
                SOCKET.send("ENDPAGE".encode('utf-8'))
                controller.up_frame('EndPage')

        def makeBoxes(event):
            for i in range(8):
                for j in range(8):
                    boxAreas[i][j] = 0
                    self.mycanvas.create_rectangle(
                        j*col_width, i*row_height, (j+1)*col_width, (i+1)*row_height, outline="black", fill="white")

        self.mycanvas.bind('<Button-1>', locate_xy)
        self.mycanvas.bind('<B1-Motion>', addLine)
        self.mycanvas.bind('<ButtonRelease-1>', clearBox)
        self.bind("<<ShowFrame>>", makeBoxes)

    def fillBox(self, col, row, color):
        col = int(col)
        row = int(row)
        boxAreas[row][col] = -1
        print(f"fill box {col} {row} {color}")
        self.mycanvas.create_rectangle(col*self.myColWidth, row*self.myRowHeight, (col+1)*self.myColWidth, (row+1)*self.myRowHeight, fill=str(color).lower())
        
        self.mycanvas.create_rectangle(col*self.myColWidth, row*self.myRowHeight,
                                       (col+1)*self.myColWidth, (row+1)*self.myRowHeight, fill=str(color).lower())

    def lockPlayersBox(self, col, row, opponent_color):
        col = int(col)
        row = int(row)
        lockedBoxes[row][col] = 1
        self.mycanvas.create_text(col*self.myColWidth + 75, row*self.myRowHeight + 56, text="DRAWING...", fill=opponent_color, font=('Helvetica 15 bold'))
    
        self.mycanvas.create_text(col*self.myColWidth + 75, row*self.myRowHeight +
                                  56, text="DRAWING...", fill=opponent_color, font=('Helvetica 15 bold'))
        # print(lockedBoxes[row][col] == 1)

    def unlockPlayersBox(self, col, row):
        col = int(col)
        row = int(row)
        lockedBoxes[row][col] = 0
        self.mycanvas.create_rectangle(col*self.myColWidth, row*self.myRowHeight, (col+1)*self.myColWidth, (row+1)*self.myRowHeight, fill='white')
        self.mycanvas.create_rectangle(col*self.myColWidth, row*self.myRowHeight,
                                       (col+1)*self.myColWidth, (row+1)*self.myRowHeight, fill='white')
        print("unlocking Boxes: ", col, row, lockedBoxes[row][col] == 0)

    def bringUpEnd(self):
        CONTROL2.up_frame('EndPage')


def startGUI():
    global WINDOW
    global GAME_WINDOW
    global END_WINDOW
    WINDOW = Tk()
    WINDOW.geometry("1200x900")
    WINDOW.rowconfigure(0, weight=1)
    WINDOW.columnconfigure(0, weight=1)
    WINDOW.resizable(False, False)
    main = MainView(WINDOW)
    GAME_WINDOW = main.get_frame("GamePage")
    END_WINDOW = main.get_frame("EndPage")
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

    # connect(args.ip, args.port)
    # connect(SERVER_IP, PORT)

    # Start GUI
    startGUI()


if __name__ == "__main__":
    main()
