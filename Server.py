import socket
import argparse
import threading

# Defaults
SERVER_IP = socket.gethostname()
SERVER = None
PORT = 9999
BUFFER = 128

MAX_CLIENTS = 4
CURR_CLIENTS = 0
FORMAT = 'utf-8'
CLIENTS = {}
LISTENING = {}

#saves players current position on the server
player_pos = [(1,1), (2,2), (3,3), (4,4)]

#Saves the players state/action on the server
player_state = ['START', 'START', 'START', 'START']

def constructrply(state, ID, pos):
    pos_str = pos_to_string(pos)
    ID_str = str(ID)
    rply = state + ':' + ID_str + ':' + pos_str
    return rply

def pos_to_string(pos):
    x = pos[0]
    y = pos[1]
    return str(x) + ',' + str(y)


def startServer(ip, port):
    global SERVER, LISTENING, CURR_CLIENTS

    # Create a TCP socket
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the server address and listen
    SERVER.bind((ip, port))
    SERVER.listen(4)
    print(f"[SERVER LIVE] listening on {ip} and port {port}")

    while CURR_CLIENTS < MAX_CLIENTS:
        # Blocking line
        client, addr = SERVER.accept()
        CLIENTS[client.fileno()] = client
        LISTENING[client.fileno()] = True
        threading.Thread(target=startListener, args=(client, CURR_CLIENTS)).start()
        CURR_CLIENTS += 1

        # receive = c.recv(BUFFER).decode(FORMAT)
        # print("Client " + str(CURR_CLIENTS) + ": " + receive)
        # broadcast("Hello")

        # TODO: close clients, decrement curr_client, remove from CLIENTS{}, stop respective client thread (if needed)


def startListener(c,player_ID):
    global SERVER, LISTENING, CURR_CLIENTS
    #Send player number to client
    c.send(f"You are Player {player_ID}".encode(FORMAT))

    while LISTENING[c.fileno()]:
        data = c.recv(BUFFER).decode(FORMAT)
        print(data)
        data = data.split(':')

        #Save players state and position to the server
        player_pos[player_ID] = eval(data[2])
        player_state[player_ID] = data[0]

        #Send other players state and position to the player
        for ID in range(4):
            if player_ID == ID:
                pass
            else:
                state = player_state[ID]
                pos = player_pos[ID]
                
                rply = constructrply(state, ID, pos)
                print(rply)
                c.sendall(rply.encode(FORMAT))

    SERVER.close()
        
    '''

        receive = c.recv(BUFFER).decode(FORMAT)
        arg = receive.split(' ')

        if (arg[0] == "STOP"):
            msg = "STOP"
            c.send(msg.encode(FORMAT))
            c.close()
            break
        elif (arg[0] == "PRINT"):
            for data in arg:
                if (data != "PRINT"):
                    print(data)
        elif (arg[0] == "PING"):
            msg = "PONG!"
            c.send(msg.encode(FORMAT))
            '''


def broadcast(msg):
    for client in CLIENTS.values():
        client.send(msg.encode(FORMAT))


def main():
    # Parse arguments
    # (usage example: Server.py --ip 192.168.0.1 --port 9999, type --help to show usage)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=SERVER_IP,
                        help="provide server ip which the clients will connect to.")
    parser.add_argument('--port', type=int, default=PORT, help="provide server port.")
    args = parser.parse_args()

    startServer(args.ip, args.port)


if __name__ == "__main__":
    main()
