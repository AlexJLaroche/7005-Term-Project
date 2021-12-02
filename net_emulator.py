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
        self.data_packet_dropped = 0
        self.ack_dropped = 0
        self.total_packets = 0



    def start_connection(self):
        self.socket = UDP.create_server(self.conf.net_address,self.conf.net_port)
        bit_error = int(input("Enter Bit error %: "))
        print("Starting to Listen...")
        while(True):
            res_packet = UDP.get_packet(self.socket)
            packet_data = pickle.loads(res_packet[0])
            print(UDP.format_packet(packet_data))
            self.total_packets += 1

            random_number = random.randint(1,100)
            if  random_number <= bit_error:
                if packet_data.packet_type == ".":
                    self.ack_dropped += 1
                else:
                    self.data_packet_dropped +=1
                print("PACKET DROPPED: ",end='')
                print(UDP.format_packet(packet_data))
                print("Number of Data Packets dropped: ", self.data_packet_dropped)
                print("Number of ACK Packets dropped: ", self.ack_dropped)
                dropped_percentage = (self.ack_dropped+self.data_packet_dropped)/self.total_packets
                print("Packets Dropped Percentage: ", dropped_percentage)

            else:
                time.sleep(self.conf.average_length)  
                if res_packet[1] == (self.conf.receive_address, self.conf.receive_port):
                    self.socket.sendto(res_packet[0], (self.conf.transmit_address, self.conf.transmit_port))
                if res_packet[1] == (self.conf.transmit_address, self.conf.transmit_port):       
                    self.socket.sendto(res_packet[0], (self.conf.receive_address, self.conf.receive_port))
            



def main():
    try:
        print('Network Running!')
        Network().start_connection()
    except KeyboardInterrupt:
        print('Network Shutting Down...')


if __name__ == "__main__":
    main()