To request a conversion from the convert_color microservice:

Import Sockets in python.

Create a socket object using socket.socket(). Use the same address family and socket type as the server. eg. 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

Use the connect() method to connect with the server. Provide the server's IP address and port number. eg
client_socket.connect(('127.0.0.1', 8888))

When accessing the convert_color server, send the rgb tuple as a string. eg
client_socket.send(','.join(map(str,hex_to_rgb(current_color))).encode())

recieve the data by specifying th emax number of bytes to recieve. eg 
response = client_socket.recv(1024)

UML Sequence Diagram:

![image](https://github.com/MasoJose/ImageManipulation/assets/114639462/aaa37789-9b7d-4899-bb27-f6590bd9a9b1)
