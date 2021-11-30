import socket
import net_config
import packets
from packets import UDP
import pickle
import random
import time
 
class Network:
    def __init__(self):
        self.conf = net_config




    def start_connection(self):
        self.socket = UDP.create_server(self.conf.net_address,self.conf.net_port)
        while(True):
            res_packet = UDP.get_packet(self.socket)
            packet_data = pickle.loads(res_packet[0])
            UDP.format_packet(packet_data)

            # Sending a reply to client
            # if packet_data.window_size == 1:
            #     if res_packet[1] == (self.conf.receive_address, self.conf.receive_port):
            #         self.socket.sendto(res_packet[0], (self.conf.transmit_address, self.conf.transmit_port))
            #     if res_packet[1] == (self.conf.transmit_address, self.conf.transmit_port):       
            #         self.socket.sendto(res_packet[0], (self.conf.receive_address, self.conf.receive_port))
            # else:
            if random.randint(1,10) != 1:  
                if res_packet[1] == (self.conf.receive_address, self.conf.receive_port):
                    self.socket.sendto(res_packet[0], (self.conf.transmit_address, self.conf.transmit_port))
                if res_packet[1] == (self.conf.transmit_address, self.conf.transmit_port):       
                    self.socket.sendto(res_packet[0], (self.conf.receive_address, self.conf.receive_port))

            else:
                print("PACKET DROPPED: ",end='')
                UDP.format_packet(packet_data)

            



def main():
    try:
        print('Network Running!')
        Network().start_connection()
    except KeyboardInterrupt:
        print('Network Shutting Down...')


if __name__ == "__main__":
    main()