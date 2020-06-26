import socket
import select
from thread import *
import sys


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server.bind(("localhost",9999)) 
#binds the server to an entered IP address and at the specified port number.

server.listen(100)

list_of_clients= {}

def broadcast(message, connection):
    for client in list_of_clients:
        if client!=connection:
            try:
                client.send(message)
            except:
                remove(client)

def broadcast_file(message, connection):
    for client in list_of_clients:
        print("entered broadcasting loop")
        if client!=connection:
            try:
                client.sendall(message) #send file content with maximum buffer size
                print("sent message\n")
            except:
                remove(client)

def remove(connection):
    if connection in list_of_clients:
        del list_of_clients[connection]

#Function to receive file from user
def fileReceive(conn):
	print ("Receiving File")

	filename = conn.recv(1024)
	print(filename)
	filename = filename[:-3]+"2.txt"
	f = open(filename, "wb")

	while True:
                print("loop entered")
		data = conn.recv(4096)
		print(data)
		if not data:
			break
		
		if "\\End" in data:
                        print("data writing")
			f.write(data[:-4])
			break
		f.write(data)
	f.close()

	print ("File received\n")
	
	fileSend(filename, conn)

def fileSend(filename, conn):
	print ("Sending file to all clients")
        print(filename)
	broadcast("\\file", conn)
        print("broadcasted file option to client")
	
        
	#Sending clients filename
	broadcast(filename, conn)
        print(filename, "broadcasted")
	#Waiting for clients to open file and be ready to write
	
        
        time.sleep(1)
	try:
		#Sending file data
                print("try block entered")
		with open(filename , "rb") as f:
                        print("data being read")
			data = f.read()
			broadcast_file(data, conn)
			print("file broadcasted")
                        time.sleep(2)
			#informing clients of EOF
			broadcast("\\End", conn)

			print("File sent to all clients\n")

		f.close()
	except:
		print("Failed to open file")
		broadcast("\\End", conn)

def clientthread(conn, name):
    conn.send("Welcome to this chatroom!\nEnter '\quit' to exit the chat room.\nEnter \\name\<new_name> to change your user name to 'new name'\nEnter \sleep\<time_to_sleep_in_seconds> to mute chat for specified time\nEnter \\black\<user_name> to blacklist a user\nEnter \unblock\<user_name> to unblock a user\nEnter \\file to send a file the the chat\n")

    while True:
            try:     
                message = conn.recv(2048)
                message.rstrip().lstrip()

                if message == "\quit":
                    remove(conn)
                    print name + " left the chat"
                    quit_notification = name + " left the chat"
                    broadcast(quit_notification, conn)
                    continue

                if message[0:6] == "\\name\\":
                    list_of_clients[conn] = message[6:]
                    print name + " changed there user name to " + message[6:]
                    name_notification = name + " changed there user name to " + message[6:]
                    broadcast(name_notification, conn)
                    name = message[6:]
                    continue

                if message == "\\file":
                    print name + ": sent a file"
                    file_notification = name + ": sent a file"
                    broadcast(file_notification, conn)
                    fileReceive(conn)

                elif message:
                    print name + ": " + message
                    message_to_send = name + ": " + message
                    broadcast(message_to_send, conn)
                else:
                    remove(conn)
            except:
                continue

while True:
    conn, addr = server.accept()
    
    conn.send("Enter your name to be shown in the chat room: ")
    name = conn.recv(1024)

    list_of_clients[conn] = name
    #maintains a dictionary of clients for ease of broadcasting a message to all online clients

    conn_notification = name + " joined the chat"
    broadcast(conn_notification, conn)
    #Broadcasts the recent connection to all active users
    
    start_new_thread(clientthread,(conn, name))
    #creates and individual thread for every user that connects

conn.close()
server.close()
