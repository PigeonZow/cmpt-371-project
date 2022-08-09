import socket
import argparse
import threading
import pickle

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

def startServer(ip, port):
    global SERVER, LISTENING, CURR_CLIENTS

    # Create a TCP socket
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the server address and listen
    SERVER.bind((ip, port))
    SERVER.listen(4)
    print(f"[SERVER LIVE] listening on {ip} and port {port}")

    while CURR_CLIENTS < MAX_CLIENTS:
        # Blocking line for accepting client connection request
        client, addr = SERVER.accept()

        # Assign client a color
        color = COLORS.pop(0)
        PLAYER_COLOR[client.fileno()] = color
        msg = color
        client.send(msg.encode('utf-8'))

        # for y in range(BOARD_HEIGHT):
        #     for x in range(BOARD_WIDTH):
        #         boxClaimedBy = BOARD[y][x].getClaimedBy()
        #         if boxClaimedBy != None:
        #             claimMsg = f"CLAIM {x} {y} {boxClaimedBy}"
        #             print(boxClaimedBy)
        #             client.send(claimMsg.encode('utf-8'))
        if CURR_CLIENTS > 0:
            claimedBoxes = []
            for y in range (BOARD_HEIGHT):
                for x in range(BOARD_WIDTH):
                    boxClaimedBy = BOARD[y][x].getClaimedBy()
                    if boxClaimedBy != None:
                        claimedBoxes.append((x, y, boxClaimedBy))
            claimedStr = pickle.dumps(claimedBoxes)
            claimMsg = f'START {claimedStr}'
            # print(claimMsg.encode('utf-8'))
            client.send(claimedStr)

        # Store reference to each client and whether they are listening
        CLIENTS[client.fileno()] = client
        LISTENING[client.fileno()] = True

        # Have a listener for each client run on separate threads
        threading.Thread(target=startListener, args=(client,)).start()

        # Increment CURR_CLIENTS
        CURR_CLIENTS += 1

        # TODO: close clients, decrement curr_client, remove from CLIENTS{}, stop respective client thread (if needed)


def fillerFunc():
    print("blah")

    
def startListener(client):
    global SERVER, LISTENING, CURR_CLIENTS
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
            # ...code for locking square at (x,y) in game state
            broadcast(f"LOCK {x} {y} {color}")
        elif (arg[0] == "UNLOCK"):
            # Client tells server that square at (x,y) is unlocked
            # UNLOCK x y
            x = arg[1]
            y = arg[2]
            color = arg[3]
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
            broadcast(f"CLAIM {x} {y} {color}")
        elif (arg[0] == "START"):
            # Client (perhaps host client?) tells server to start the game
            fillerFunc()
            # ...code to start game
        elif (arg[0] == "RESTART"):
            # Client tells server to restart game
            fillerFunc()
            # ...code to reset game state
        elif (arg[0] == "END"):
            # Client tells server to end game (perhaps the player who wins sends the message?)
            fillerFunc()
            # ...code to end game

def broadcast(msg):
    # Broadcast msg to all connected clients
    msg = msg
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
