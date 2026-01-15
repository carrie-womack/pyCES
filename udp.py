import socket
import time
import config

class UDPaddr:
    def __init__(self, server_IP, server_port, client_IP, client_port, UDP_buffer):
        self.server_IP = server_IP
        self.server_port = server_port
        self.client_IP = client_IP
        self.client_port = client_port
        self.buffer = UDP_buffer

def configure_UDP():

    config_data = config.open_config()

    SERVER_IP = config_data["UDP"]["server_IP"]
    SERVER_PORT = config_data["UDP"]["server_port"]
    CLIENT_IP = config_data["UDP"]["client_IP"]
    CLIENT_PORT = config_data["UDP"]["client_port"]
    BUFFER_SIZE = config_data["UDP"]["buffer_size"]

    myUDPaddr = UDPaddr(SERVER_IP, SERVER_PORT, CLIENT_IP, CLIENT_PORT, BUFFER_SIZE)

    return myUDPaddr

def open_UDP_server(myUDPaddr):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(0.1)

    # Bind the socket to the address and port
    server_socket.bind((myUDPaddr.server_IP, myUDPaddr.server_port))

    return server_socket

def clear_buffer(socket, myUDPaddr):

    current_timeout = socket.gettimeout()
    socket.settimeout(0.0)
    while True:
        try:
            data, address = socket.recvfrom(myUDPaddr.buffer)
            message = data.decode('utf-8')
            print("dumping message: {message}")
        except OSError:
            break
    
    socket.settimeout(current_timeout)

def main():

    myUDPaddr = configure_UDP()

    print(f"UDP Server broadcasting on {myUDPaddr.server_IP}:{myUDPaddr.server_port}")

    myserver = open_UDP_server(myUDPaddr)

    client_address = (myUDPaddr.client_IP, myUDPaddr.client_port)   

    while True:
        try:
            try:
                # Receive data and sender's address
                data, address = myserver.recvfrom(myUDPaddr.buffer)
                message = data.decode('utf-8')
                print(f"Received from {address}: {message}")

                if "Also, " in message:
                    print("\t\tInstructions received")
            except TimeoutError:
                print("\tIs anyone out there?")
                time.sleep(1)

            # Prepare and send a response
            response_message = f"Here is the status report you wanted"
            myserver.sendto(response_message.encode('utf-8'), client_address)
            print(f"Sent response to {client_address}: '{response_message}'")
        except KeyboardInterrupt:
            print("\tStopping...")
            myserver.close()
            break

if __name__ == '__main__':
    main()