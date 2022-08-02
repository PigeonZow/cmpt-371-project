import socket
import argparse
import threading

# Defaults
BUFFER = 128
PORT = 9999
SERVER_IP = socket.gethostname()
LISTENING = True


def startListener(s):
    global LISTENING
    while LISTENING:
        receive = s.recv(BUFFER).decode('utf-8')
        arg = receive.split(':')
        if (arg[0] == "START"):
            print("State: ", arg[0], "Player: ", arg[1], "Position: ", arg[2])
        else:
            print(receive)

    s.close()


def startInput(s):
    global LISTENING
    while LISTENING:
        msg = input()
        s.send(msg.encode('utf-8'))


def connect(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    print(f"[CONNECTED] to {ip}")

    threading.Thread(target=startListener, args=(s,)).start()
    threading.Thread(target=startInput, args=(s,)).start()


def main():
    # Parse arguments
    # (usage example: Client.py --ip 192.168.0.1 --port 9999)
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=SERVER_IP)
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()

    connect(args.ip, args.port)


if __name__ == "__main__":
    main()
