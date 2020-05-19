from socket import *

serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
serverHost = gethostname()

clientSocket.connect((serverHost,serverPort))

while True:
    rcvMessage = clientSocket.recv(2048).decode('utf-8')
    if rcvMessage != "\0":
        print(rcvMessage)
    message = input("\n<Me>: ")
    if message == '.exit':
        clientSocket.send(message.encode('utf-8'))
        print(clientSocket.recv(2048).decode('utf-8'))
        break
    elif message == '':
        clientSocket.send(('\0').encode('utf-8'))
    else:
        clientSocket.send(message.encode('utf-8'))
clientSocket.close()
