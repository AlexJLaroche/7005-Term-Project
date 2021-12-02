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
        self.seq_num = 0
        self.ack_num = 0
        self.packet_list = []
        # self.rx_buffer_seq = []
        self.rx_buffer_ack = []
        self.rx_buffer_packets = []
        self.received_data = []
        self.pre_ack = 0
        self.dup_ack = 0
        self.num_send_ack = 0

    # Try and remove?
    def create_packet(self, packet_type,window_size,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.receive_address, self.conf.receive_port, self.conf.transmit_address, self.conf.transmit_port, packet_type, seq_num, p_data, window_size, ack_num)
        return packet


    def receive_data(self):
        # RECEIVE PUSH ACK
        packet_PSH_ACK = UDP.get_packet(self.socket)
        packet_PSH_ACK_data = pickle.loads(packet_PSH_ACK[0])
        if packet_PSH_ACK_data.seq_num != self.ack_num:
            print("Duplicate ACK: ", end="")
            logging.info("Duplicate ACK: ",)
            self.dup_ack += 1
        print(UDP.format_packet(packet_PSH_ACK_data))
        logging.info(UDP.format_packet(packet_PSH_ACK_data))
        
        

        self.ack_num = packet_PSH_ACK_data.seq_num + len(packet_PSH_ACK_data.data)
        self.seq_num = packet_PSH_ACK_data.ack_num
        # for i in self.received_data:
        #     if self.received_data[i] == self.seq_num:
        #         print('Duplicate ACK: ')
        #         UDP.format_packet(packet_PSH_ACK_data)
        packet_ACK = self.create_packet(".", packet_PSH_ACK_data.window_size, seq_num=self.seq_num, ack_num=self.ack_num, p_data="0")
        print(UDP.format_packet(packet_ACK))
        logging.info(UDP.format_packet(packet_ACK))
        UDP.send_packet(self.socket, packet_ACK)
        self.num_send_ack +=1
        if packet_PSH_ACK_data.packet_type == "E":
            raise Exception("EOT Received")


    def start_connection(self):
        self.socket = UDP.create_server(self.conf.receive_address, self.conf.receive_port)
        receiver_listen = True
        while receiver_listen:
            try:
                self.receive_data()
            except Exception as e:
                logging.info('EOT Received')
                logging.info("Number of sent ACKs: {}".format(self.num_send_ack))
                print(e)
                


def main():
    print('Receiver Running!')
    Receiver().start_connection()


if __name__ == "__main__":
    main()