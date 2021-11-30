import socket
import pickle
import packets
import receiver_config
from packets import UDP

class Receiver:
    def __init__(self):
        self.conf = receiver_config
        self.seq_num = 0
        self.ack_num = 0
        self.packet_list = []
        self.rx_buffer_seq = 0
        self.rx_buffer_ack = 0
        self.rx_buffer_packets = []

    # Try and remove?
    def create_packet(self, packet_type,window_size,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.receive_address, self.conf.receive_port, self.conf.transmit_address, self.conf.transmit_port, packet_type, seq_num, p_data, window_size, ack_num)
        return packet

    def SOT(self):
        # RECEIVE SYN PACKET
        # seq = 0, ack = none
        packet_SYN = UDP.get_packet(self.socket)
        packet_SYN_data = pickle.loads(packet_SYN[0])
        UDP.format_packet(packet_SYN_data)
        # if packet_SYN_data.packet_type == "S":

        # SEND SYN/ACK PACKET
        # seq = 0, ack = 1

        
        self.ack_num = packet_SYN_data.seq_num + 1
        packet_SYN_ACK = self.create_packet("S.",1,seq_num=self.seq_num, ack_num=self.ack_num)
        UDP.format_packet(packet_SYN_ACK)
        UDP.send_packet(self.socket, packet_SYN_ACK)

        # RECEIVE ACK PACKET
        # seq = 1, ack = 1
        packet_ACK = UDP.get_packet(self.socket)
        packet_ACK_data = pickle.loads(packet_ACK[0])
        UDP.format_packet(packet_ACK_data)

        self.seq_num = packet_ACK_data.ack_num
        self.ack_num = packet_ACK_data.seq_num



    def receive_data(self):
        # RECEIVE PUSH ACK
        packet_PSH_ACK = UDP.get_packet(self.socket)
        packet_PSH_ACK_data = pickle.loads(packet_PSH_ACK[0])
        UDP.format_packet(packet_PSH_ACK_data)

        self.ack_num = packet_PSH_ACK_data.seq_num + len(packet_PSH_ACK_data.data)
        self.seq_num = packet_PSH_ACK_data.ack_num
        
        packet_ACK = self.create_packet(".", packet_PSH_ACK_data.window_size, seq_num=self.seq_num, ack_num=self.ack_num, p_data="0")
        UDP.format_packet(packet_ACK)
        UDP.send_packet(self.socket, packet_ACK)
        if packet_PSH_ACK_data.packet_type == "E":
            raise Exception("EOT Received")


    def start_connection(self):
        self.socket = UDP.create_server(self.conf.receive_address, self.conf.receive_port)
        receiver_listen = True
        while receiver_listen:
            try:
                self.receive_data()
            except Exception as e:
                print(e)
                print("Closing connection..")
                


def main():
    print('Receiver Running!')
    Receiver().start_connection()


if __name__ == "__main__":
    main()