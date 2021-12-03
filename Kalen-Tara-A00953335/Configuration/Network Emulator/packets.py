import socket
import pickle
import packets

bufferSize = 1024
# FLAGS/packet_type
# S  = Start of Transmission
# P. = Push ACKs (Data being Sent)
# .  = ACK, Data has been received
# E  = End of Transmission
#
# Packet Obj Structure:
#{
#   src_address: string
#   src_port: int
#   dst_address: string
#   dst_port: int
#   packet_type: string
#   seq_num: int
#   ack_num: int
#   data: string
#   window_size: int
# }
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

    # ---Function: create_server----
    # Return a socket created binded with the specified address and port
    def create_server(address, port):
        UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPClientSocket.bind((address,port)) 
        return UDPClientSocket

    # ---Function: get_packet----
    # Returns the packet received from buffer
    def get_packet(socket):
        packet = socket.recvfrom(bufferSize)
        return packet

    # ---Function: send_packet----
    # Sends the specified packet to the network using the specified sockett
    def send_packet(socket,packet,network):
            bytesToSend = pickle.dumps(packet)
            socket.sendto(bytesToSend, network)

    # ---Function: send_packet----
    # Return a string formatted with all the packet information 
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
        return packet_string
        
