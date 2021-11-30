import socket
import pickle
import packets
net_address = '127.0.0.1'
net_port = 20001

bufferSize = 1024
# FLAGS
# S  = SYN
# S. = SYN/ACK
# .  = ACK
# P. = PSH/ACK
# F. = FIN/ACK
#
class Packet:
    def __init__(self, src_address, src_port, dst_address, dst_port, packet_type, seq_num, data, window_size, ack_num):
        self.src_address = src_address
        self.src_port = src_port
        self.dst_address = dst_address
        self.dst_port = dst_port
        self.packet_type = packet_type
        self.seq_num = seq_num
        self.data = data
        self.window_size = window_size
        self.ack_num = ack_num

class UDP:
    def __init__():
        pass


    def create_server(address, port):
        UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPClientSocket.bind((address,port)) 
        return UDPClientSocket

    def get_packet(socket):
        packet = socket.recvfrom(bufferSize)
        return packet

    def send_packet(socket,packet):
            bytesToSend = pickle.dumps(packet)
            socket.sendto(bytesToSend, (net_address, net_port))
    
    def create_packet(self,packet_type,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.receive_address, self.conf.receive_port, self.conf.transmit_address, self.conf.transmit_port, packet_type, seq_num, p_data, self.conf.window_size, ack_num)
        return packet

    def format_packet(packet):
        src_address = packet.src_address
        src_port = packet.src_port
        dst_address = packet.dst_address
        dst_port = packet.dst_port
        flag = packet.packet_type
        seq_num = packet.seq_num
        ack_num = packet.ack_num
        window_size = packet.window_size
        data = len(packet.data)
        
        packet_string = "IP {}:{} > {}:{}: Flags [{}], seq {}, ack {}, win {}, length {} ".format(src_address, src_port, dst_address, dst_port, flag, seq_num, ack_num, window_size, data)
        print(packet_string)
