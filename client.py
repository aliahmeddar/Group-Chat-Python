import socket
import select
import sys
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server.connect(("localhost",9999))
blocked = []

def filesend(filename):							
	server.send("\\file")				
	time.sleep(2)							

	server.send(filename)				
	time.sleep(2)
	
	try:
		with open(filename, "rb") as f:
			print ("Sending file to server")

			data = f.read()
			server.sendall(data)

			#Notifying server of EOF
			server.send("\\End")
			print("Done sending file")
		
		#closing the file after reading
		f.close()
	except:
		print("Failed to open file")
		time.sleep(2)
		server.send("\\End")

def filereceive(sock):
	print ("Receiving a file")
        time.sleep(2)
	filename = sock.recv(1024)
	print(filename)
	f = open(filename, "w")

	while True:
                print("in loop")
		data = sock.recv(4096)
		print(data)
		if not data:
			break

		if "\\End" in data:
                        print("writing")
			f.write(data[:-4]).encode('utf-8')
			break

		f.write(data)

	f.close()
	print ("File received")

while True:
    sockets_list = [sys.stdin, server]
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])
    for sock in read_sockets:
        if sock == server:
            message = sock.recv(2048)
            if (":" in message) and (message[:message.index(":")] in blocked):
                continue

            if message == "\\file":
                
                filereceive(sock)

            print message

            
        
        else:
            message = sys.stdin.readline().rstrip().lstrip()

            if message == "\quit":
                server.send(message)
                server.shutdown(socket.SHUT_RDWR)
                server.close()
                sys.exit()

            if message[0:7] == "\sleep\\":
                time.sleep(int(message[7:]))
                
            if message[0:7] == "\\black\\":
                blocked.append(message[7:])
                continue

            if message[0:9] == "\\unblock\\":
                if message[9:] in blocked:
                    blocked.remove(message[9:])

            if message == "\\file":
                print("Enter file name:")
                filename = sys.stdin.readline().rstrip().lstrip()
                filesend(filename)
                continue

            else:
                server.send(message)
            
server.close()
