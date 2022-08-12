import socket
import argparse
import threading
import time
# Defaults
SERVER_IP = socket.gethostname()
SERVER = None
PORT = 9999
BUFFER = 1024

MAX_CLIENTS = 4
CURR_CLIENTS = 0
CLIENTS = {}
LISTENING = {}

BOARD_HEIGHT = 8
BOARD_WIDTH = 8

COLORS = ["RED", "BLUE", "GREEN", "YELLOW"]
PLAYER_COLOR = {}
BOARD = []
boxColors = []

class Box():
    # Custom Box object
    def __init__(self):
        self.LOCKED = False
        self.CLAIMED_BY = None

    def lock(self):
        self.LOCKED = True

    def unlock(self):
        self.LOCKED = False

    def claim(self, color):
        self.CLAIMED_BY = color

    def getClaimedBy(self):
        return self.CLAIMED_BY

    def getLocked(self):
        return self.LOCKED

    def print(self):
        print(str(self.LOCKED) + "\n" + str(self.CLAIMED_BY))

def updateBoard(client):
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            boxClaimedBy = BOARD[y][x].getClaimedBy()
            if boxClaimedBy != None:
                claimMsg = f"CLAIM {x} {y} {boxClaimedBy}"
                print("BOX CLAIMED BY",boxClaimedBy)
                client.send(claimMsg.encode('utf-8'))
                time.sleep(0.05)

def startServer(ip, port):
    global SERVER, LISTENING, CURR_CLIENTS

    # Create a TCP socket
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the server address and listen
    SERVER.bind((ip, port))
    SERVER.listen(4)
    print(f"[SERVER LIVE] listening on {ip} and port {port}")

    while CURR_CLIENTS <= MAX_CLIENTS:
        try:
            # Blocking line for accepting client connection request
            client, addr = SERVER.accept()
        except:
            print("Loop break")
            SERVER.close()
            break

        # Assign client a color
        color = COLORS.pop(0)
        PLAYER_COLOR[client.fileno()] = color
        msg = color
        client.send(msg.encode('utf-8'))

        # Store reference to each client and whether they are listening
        CLIENTS[client.fileno()] = client
        LISTENING[client.fileno()] = True

        # Have a listener for each client run on separate threads
        threading.Thread(target=startListener, args=(client,)).start()

        # Increment CURR_CLIENTS
        CURR_CLIENTS += 1

    print("\n[SERVER CLOSED] all connections ended.")


def fillerFunc():
    print("blah")


def saveboxColors(clr):
    boxColors.append(clr)


def chooseWinner():
    return max(boxColors, key=boxColors.count)

    
def startListener(client):
    global SERVER, LISTENING, CURR_CLIENTS
    updateBoard(client)
    while LISTENING[client.fileno()]:
        receive = client.recv(BUFFER).decode('utf-8')
        arg = receive.split(' ')

        if (arg[0] == "STOP"):
            # Will cause exception messages
            msg = "STOP"
            LISTENING[client.fileno()] = False
            client.send(msg.encode('utf-8'))
            for client in CLIENTS.values():
                client.close()
            SERVER.close()
            break
        elif (arg[0] == "DISCONNECT"):
            # Client/User disconnects from server
            msg = "DISCONNECT"
            CURR_CLIENTS -= 1
            COLORS.append(PLAYER_COLOR[client.fileno()])
            LISTENING[client.fileno()] = False
            client.send(msg.encode('utf-8'))
            client.close()
            break
        elif (arg[0] == "PRINT"):
            # Test function
            for data in arg:
                if (data != "PRINT"):
                    print(data)
        elif (arg[0] == "PING"):
            # Test function
            msg = "PONG!"
            client.send(msg.encode('utf-8'))
        elif (arg[0] == "LOCK"):
            # Client tells server that square at (x,y) is locked
            # LOCK x y
            x = arg[1]
            y = arg[2]
            color = arg[3]
            row = int(y)
            col = int(x)
            BOARD[row][col].lock()
            BOARD[row][col].print()
            print(f'row: {row}, col: {col} locked')
            # ...code for locking square at (x,y) in game state
            broadcast(f"LOCK {x} {y} {color}")
        elif (arg[0] == "UNLOCK"):
            # Client tells server that square at (x,y) is unlocked
            # UNLOCK x y
            x = arg[1]
            y = arg[2]
            color = arg[3]
            row = int(y)
            col = int(x)
            BOARD[row][col].unlock()
            BOARD[row][col].print()
            print(f'row: {row}, col: {col} unlocked')
            # ...code for unlocking square at (x,y) in game state
            broadcast(f"UNLOCK {x} {y} {color}")
        elif (arg[0] == "CLAIM"):
            # Client tells server that they claim the square at (x,y)
            # CLAIM x y
            x = arg[1]
            y = arg[2]
            color = arg[3]
            # ...code for claiming square at (x,y) in game state
            # check for whether client has claimed 50% of the square should be done on client side(?)
            col = int(x)
            row = int(y)
            BOARD[row][col].claim(color)
            BOARD[row][col].print()
            # are all 64 boxes taken if yes end game
            print(f'row: {row} col {col} claimed by {color}')
            broadcast(f"CLAIM {x} {y} {color}")
            saveboxColors(color)
        elif (arg[0] == "START"):
            # Client (perhaps host client?) tells server to start the game
            fillerFunc()
            # ...code to start game
        elif (arg[0] == "RESTART"):
            # Client tells server to restart game
            fillerFunc()
            # ...code to reset game state
        elif (arg[0] == "ENDPAGE"):
            msg = "ENDPAGE " + chooseWinner()
            broadcast(msg)
        elif (arg[0] == "END"):
            # Client tells server to end game (perhaps the player who wins sends the message?)
            # ...code to end game
            msg = "END " + chooseWinner()
            LISTENING[client.fileno()] = False
            CURR_CLIENTS -= 1
            client.send(msg.encode('utf-8'))
            client.close()
            break
    print(f"CC: {CURR_CLIENTS}")
    if CURR_CLIENTS < 1:
        SERVER.close()

def broadcast(msg):
    # Broadcast msg to all connected clients
    for client in CLIENTS.values():
        client.send(msg.encode('utf-8'))


def createBoard():
    global BOARD

    # Create Box object for each square in game board and store reference in BOARD 2D array
    for y in range(BOARD_HEIGHT):
        row = []
        for x in range(BOARD_WIDTH):
            newBox = Box()
            row.append(newBox)
        BOARD.append(row)

    BOARD[0][0].print()


def main():
    # Parse arguments
    # (usage example: Server.py --ip 192.168.0.1 --port 9999, type --help to show usage)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=SERVER_IP,
                        help="provide server ip which the clients will connect to.")
    parser.add_argument('--port', type=int, default=PORT, help="provide server port.")
    args = parser.parse_args()

    # Initialize game board
    createBoard()

    # Start server
    startServer(args.ip, args.port)


if __name__ == "__main__":
    main()
