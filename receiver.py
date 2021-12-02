import socket
import pickle
import packets
import receiver_config
from packets import UDP
import logging

logging.basicConfig(filename='Receiver.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)

class Receiver:
    def __init__(self):
        self.conf = receiver_config
        self.net = (self.conf.net_address,self.conf.net_port)
        self.seq_num = 0
        self.ack_num = 0
        self.packet_list = []
        self.rx_buffer_ack = []
        self.rx_buffer_packets = []
        self.received_data = []
        self.pre_ack = 0
        self.dup_ack = 0
        self.num_send_ack = 0

    # ---Function: create_packet----
    # Returns a packet Object with the specific required entries
    def create_packet(self, packet_type,window_size,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.receive_address, self.conf.receive_port, self.conf.transmit_address, self.conf.transmit_port, packet_type, seq_num, p_data, window_size, ack_num)
        return packet

    # ---Function: receive_data----
    # 1. Listens for packets; PUSH ACKs
    # 2. If packet is out of order, ADD 1 to duplicate ack
    # 3. Increment the the Acknowledgement number by the Sequence number 
    #    and the length of data
    # 4. Create an ACK packet (".") and send the packet to the network emulator. 
    # 5. If the Packet Type is "E" then raise an exception which logs the Number 
    #    of sent ACKs over the transmittion.
    def receive_data(self):
        packet_PSH_ACK = UDP.get_packet(self.socket) #1
        packet_PSH_ACK_data = pickle.loads(packet_PSH_ACK[0])
        if packet_PSH_ACK_data.seq_num != self.ack_num: #2
            print("Duplicate ACK: ", end="")
            logging.info("Duplicate ACK: ",)
            self.dup_ack += 1
        print(UDP.format_packet(packet_PSH_ACK_data))
        logging.info(UDP.format_packet(packet_PSH_ACK_data))
        
        

        self.ack_num = packet_PSH_ACK_data.seq_num + len(packet_PSH_ACK_data.data) #3
        self.seq_num = packet_PSH_ACK_data.ack_num

        packet_ACK = self.create_packet(".", packet_PSH_ACK_data.window_size, seq_num=self.seq_num, ack_num=self.ack_num, p_data="0") #4
        print(UDP.format_packet(packet_ACK))
        logging.info(UDP.format_packet(packet_ACK))
        UDP.send_packet(self.socket, packet_ACK,self.net)
        self.num_send_ack +=1
        if packet_PSH_ACK_data.packet_type == "E":#5
            raise Exception("EOT Received")

    # ---Function: start_connection----
    # 1. Initializes a server and binds it to the network addess and port 
    #    specified in the configuration file.
    # 2. While the receiver is listening, Allow Packets to be Receieved
    # 3. If the Packet Type is "E" then raise an exception which logs the Number 
    #    of sent ACKs over the transmittion.
    def start_connection(self):
        self.socket = UDP.create_server(self.conf.receive_address, self.conf.receive_port)#1
        receiver_listen = True#2
        while receiver_listen:
            try:
                self.receive_data()
            except Exception as e:#3
                logging.info('EOT Received')
                logging.info("Number of sent ACKs: {}".format(self.num_send_ack))
                print(e)
                


def main():
    print('Receiver Running!')
    Receiver().start_connection()


if __name__ == "__main__":
    main()