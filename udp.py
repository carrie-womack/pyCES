import socket
import time
import config

class UDPaddr:
    def __init__(self, UDP_IP, UDP_port, UDP_buffer):
        self.IP = UDP_IP
        self.port = UDP_port
        self.buffer = UDP_buffer

def configure_UDP():

    config_data = config.open_config()

    SERVER_IP = config_data["UDP"]["IP"]
    SERVER_PORT = config_data["UDP"]["port"]
    BUFFER_SIZE = config_data["UDP"]["buffer_size"]

    myUDPaddr = UDPaddr(SERVER_IP, SERVER_PORT, BUFFER_SIZE)

    return myUDPaddr

def open_UDP_server(myUDPaddr):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(0.1)

    # Bind the socket to the address and port
    server_socket.bind((myUDPaddr.IP, myUDPaddr.port))

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

    print(f"UDP Server listening on {myUDPaddr.IP}:{myUDPaddr.port}")

    myserver = open_UDP_server(myUDPaddr)    

    while True:
        try:
            try:
                # Receive data and sender's address
                data, address = myserver.recvfrom(myUDPaddr.buffer)
                message = data.decode('utf-8')
                print(f"Received from {address}: {message}")

                # Prepare and send a response
                response_message = f"Here is the status report you wanted"
                myserver.sendto(response_message.encode('utf-8'), address)
                print(f"Sent response to {address}: '{response_message}'")

                if "Also, " in message:
                    print("\t\tInstructions received")
            except TimeoutError:
                print("\tIs anyone out there?")
                # time.sleep(0.5)
        except KeyboardInterrupt:
            print("\tStopping...")
            myserver.close()
            break

if __name__ == '__main__':
    main()