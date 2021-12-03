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

# ---Function: start_connection----
# 1. Initializes a server and binds it to the network address and port 
#    specified in the configuration file.
# 2. The User is then prompted a required input where they must specify 
#    the Bit Rate Error Percentage.
# 3. While there is a connection, listen for packets.
# 4. When the packets arrive, determine if the packet is dropped (Specified by Bit Error Rate)
# 5. If the packet is lost, simply print the lost packet and return to listening for packets
# 6. If the packet is NOT lost, then send the Receiver message to the Transmitter or send the 
#    Transmitter message to the Receiver. 
    def start_connection(self):
        self.socket = UDP.create_server(self.conf.net_address,self.conf.net_port) #1
        bit_error = int(input("Enter Bit error %: ")) #2
        print("Starting to Listen...")
        connection = True
        while(connection): #3
            res_packet = UDP.get_packet(self.socket)
            packet_data = pickle.loads(res_packet[0])
            print(UDP.format_packet(packet_data))
            self.total_packets += 1

            random_number = random.randint(1,100) #4
            if  random_number <= bit_error: #5 
                if packet_data.packet_type == ".":
                    self.ack_dropped += 1
                else:
                    self.data_packet_dropped +=1
                print("PACKET DROPPED: ",end='')
                print(UDP.format_packet(packet_data))
                print("Number of Data Packets dropped: ", self.data_packet_dropped)
                print("Number of ACK Packets dropped: ", self.ack_dropped)
                dropped_percentage = ((self.ack_dropped+self.data_packet_dropped)/self.total_packets)*100
                print("Packets Dropped Percentage: {}%".format(dropped_percentage))

            else: #6
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