from socket import *
from random import randint
import select

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverHost = gethostname()
serverSocket.bind((serverHost,serverPort))

print("The server is up and running.\n")

serverSocket.listen(25)

socketList = []
clientList = []
conversationList = []

socketList.append(serverSocket)

def createClientId(clientSocket):
    if len(clientList) == 50:
        print("Sorry no more room in app\n")
        return
    idNotAssigned = True
    while (idNotAssigned):
        n = randint(1,50)
        id = "User"+str(n)
        if not any(client.get('id') == id for client in clientList):
            clientList.append({"user":clientSocket,"id":id})
            idNotAssigned = False
    return

def createConversation(clientSocketA,clientSocketB):
    if isInConversation(clientSocketA):
        message = "Can't create conversation, you are already in on.\n"
        return message
    if isInConversation(clientSocketB):
        message = "Sorry but that user is in a Conversation.\n"
        return message

    messageA = "Creating Conversation with "+getID(clientSocketB)+", type your first message.\n Press Enter to refresh chat and see new message, These blank messages won't send.\n.end to leave chat and .exit to exit server \n"
    messageB = getID(clientSocketA)+" is creating a conversation with you.\n Press Enter to refresh chat and see new message, These blank messages won't send.\n.end to leave chat and .exit to exit server \n"
    clientSocketB.send(messageB.encode('utf-8'))
    conversationList.append((clientSocketA,clientSocketB))
    return messageA

def getConversationPartner(socket):
    for conversation in conversationList:
        if socket in conversation:
            for client in conversation:
                if client != socket:
                    return client
    return

def endConversation(socket):
    for conversation in conversationList:
        if socket in conversation:
            conversationList.remove(conversation)
    return

def isInConversation(socket):
    if any(socket in conversation for conversation in conversationList):
        return True
    else:
        return False
    return

def getID(socket):
    for client in clientList:
        if client.get('user') == socket:
            return client.get('id')
    return

def getClient(userId):
    for client in clientList:
        if client.get('id') == userId:
            return client.get('user')
    return

def listClients(clientSocket):
    message = "\nUser List:\n"
    for client in clientList:
        if client.get('user') != clientSocket:
            message += client.get('id')+'\n'
    return message

def removeClient(clientSocket):
    for client in clientList:
        if client.get('user') == clientSocket:
            clientList.remove(client)
            if clientSocket in socketList:
                socketList.remove(clientSocket)
    return

while True:
    toRead,toWrite,error = select.select(socketList,[],[],0)

    for socket in toRead:
        if socket == serverSocket:
            clientSocket, address = socket.accept()
            socketList.append(clientSocket)
            createClientId(clientSocket)
            print(address[0] + ' connected.\n' )
            message = '\nThank you for connecting!\nChat commands are .list, .exit, .chat <User>\n'
            message += listClients(clientSocket)
            clientSocket.send(message.encode('utf-8'))
        else:
            input = socket.recv(2048).decode('utf-8')
            if isInConversation(socket):
                target = getConversationPartner(socket)
                if input == "\0":
                    message = ""
                    socket.send(message.encode('utf-8'))
                    target.send(message.encode("utf-8"))
                elif input == ".end":
                    message = "\nConversation is ending"
                    endConversation(socket)
                    socket.sendall(message.encode('utf-8'))
                    target.sendall(message.encode('utf-8'))
                elif input == ".exit":
                    message = "\n Leaving Chat Server. \n"
                    socket.sendall(message.encode('utf-8'))
                    message = "\n"+getID(socket)+" has left the server. Ending conversation."
                    target.sendall(message.encode('utf-8'))
                    endConversation(socket)
                    removeClient(socket)
                else:
                    message = "\n<"+getID(socket)+">: "+input
                    target = getConversationPartner(socket)
                    target.send(message.encode("utf-8"))
            else:
                if input == ".list":
                    message = listClients(socket)
                    socket.send(message.encode('utf-8'))
                elif input == ".exit":
                    message = "\n Leaving Chat Server. \n"
                    socket.send(message.encode('utf-8'))
                    removeClient(socket)
                elif ".chat" in input:
                    messageParts = input.split()
                    if len(messageParts) != 2:
                        message = "\n Incorrect usage of command. \n"
                        socket.send(message.encode('utf-8'))
                    else:
                        socketB = getClient(messageParts[1])
                        message = createConversation(socket,socketB)
                        socket.send(message.encode('utf-8'))
                else:
                    message = "\0"
                    socket.send(message.encode('utf-8'))
