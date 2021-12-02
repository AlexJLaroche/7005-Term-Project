import socket
import packets
import pickle
import transmit_config
from packets import UDP
import logging
logging.basicConfig(filename='Transmitter.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO)


class Transmitter:
    def __init__(self):
        self.conf = transmit_config
        self.seq_num = 0
        self.ack_num = 0
        self.sep_data = []
        self.expected_ack = []
        self.tx_buffer_seq = 0
        self.tx_buffer_ack = 0
        self.buffer_expected_ack = []
        self.buffer_sender_data = []
        self.order = True
        self.window_size = 1
        self.packet_loss_occurred = False
        self.num_packets_sent=0
        self.num_packets_resent=0

# Create a UDP socket at client side
    #  Try and remove?
    def create_packet(self, packet_type,window_size,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.transmit_address, self.conf.transmit_port, self.conf.receive_address, 
        self.conf.receive_port, packet_type, seq_num, p_data, window_size, ack_num)
        return packet



    def transmit(self,data,packet_type):
        e = 0
        while e < len(data):
        # for e in range(0,len(data),self.window_size):
            i=0
            self.tx_buffer_seq = self.seq_num
            self.tx_buffer_ack = self.ack_num
            while len(data[e+i:]) % self.window_size != 0:
                data.append('.')
            while i < self.window_size:
                self.send_data(data[e+i],packet_type)
                self.num_packets_sent+=1
                # print(data[e+i])
                # print(data[e+i:])
                i += 1
            self.buffer_expected_ack = self.expected_ack.copy()
            self.window_ack()
            self.buffer_sender_data = []
            # if self.packet_loss_occurred == True:
            #     if self.window_size == self.conf.window_size or self.window_size == self.conf.window_size/2:
            #         self.window_size = self.window_size/4
            #     self.packet_loss_occurred = False
            
            if packet_type == "S":
                e+=1
            else:
                if self.window_size < self.conf.window_size:
                    self.window_size = self.window_size * 2
                else:
                    self.window_size = self.conf.window_size
                e = e + self.window_size
            
            


    def send_data(self, data, packet_type):
        #p_data="0d0a0d0a537465776172742c200d0a0d0a4f422e20412e442e20313839322e20"
        # SEND PUSH ACK PACKET
        packet_PSH_ACK = self.create_packet(packet_type, self.window_size, seq_num=self.seq_num, ack_num=self.ack_num, p_data=data)
        print(UDP.format_packet(packet_PSH_ACK))
        logging.info(UDP.format_packet(packet_PSH_ACK))
        UDP.send_packet(self.socket, packet_PSH_ACK)
        self.seq_num = self.seq_num + len(packet_PSH_ACK.data)
        self.buffer_sender_data.append(packet_PSH_ACK)

        ack_num = packet_PSH_ACK.seq_num + len(packet_PSH_ACK.data)
        seq_num = packet_PSH_ACK.ack_num
        self.expected_ack.append(ack_num)


        ## Receive ack until it gets one that is unexpected it will end the loop and restart it 
    def receive_ack(self):
        # RECEIVE ACK PACKET
        self.socket.settimeout(self.conf.timeout)
        try:
            receiver_res = UDP.get_packet(self.socket)
            packet_ACK = pickle.loads(receiver_res[0])
            print(UDP.format_packet(packet_ACK))
            logging.info(UDP.format_packet(packet_ACK))
            self.ack_num = packet_ACK.seq_num + len(packet_ACK.data)
            self.seq_num = packet_ACK.ack_num 
        except socket.timeout as e:
            self.order = False
            print("SOCKET TIMED OUT RETRANSIMTTING.....")
            logging.info('SOCKET TIMED OUT RETRANSIMTTING.....')
            

    def retransmit_packets(self):
        self.order = True
        self.packet_loss_occurred = True
        # self.transmit(self.buffer_sender_data, "P.")
        logging.info('Retransmitting: ')
        self.num_packets_resent = self.num_packets_resent + len(self.buffer_sender_data)
        for i in self.buffer_sender_data:
            print('Retransmitting: ', end="")
            print(UDP.format_packet(i))
            logging.info(UDP.format_packet(i))
            UDP.send_packet(self.socket, i)

        
    def window_ack(self):
        o = 0
        while o < self.window_size:
            if self.order == False:
                break
            else:
                self.receive_ack()
            o += 1
        if self.order == False:
            self.seq_num = self.tx_buffer_seq
            self.ack_num = self.tx_buffer_ack
            self.expected_ack = self.buffer_expected_ack.copy()
            self.retransmit_packets()
            self.window_ack()

    def split_data(self,data):
        n = self.conf.max_packet_size
        list_data= [data[i:i+n] for i in range(0, len(data), n)]
        # while len(list_data) % self.window_size != 0:
        #     list_data.append('.')
        self.sep_data = list_data
    


    def start_connection(self):
        self.socket = UDP.create_server(self.conf.transmit_address, self.conf.transmit_port)
        print("Starting Connection...")
        self.transmit(".", "S")      
        
        print("Connection Established...")
        connection = True
        while connection:
            try:
                enter_data =  input('Enter Data to Sender: ')
                self.split_data(enter_data)
                self.transmit(self.sep_data,"P.")
            except KeyboardInterrupt:
                self.window_size = 1
                self.transmit(".","E")
                print('Transmitter Shutting Down...')
                logging.info('Transmitter Shutting Down...')
                print("Total Packets Sent: {}".format(self.num_packets_sent))
                logging.info("Total Packets Sent: {}".format(self.num_packets_sent))
                print("Total Packets Re-Sent: ", self.num_packets_resent)
                logging.info("Total Packets Re-Sent: {}".format(self.num_packets_resent))
                quit()


def main():
    print('Transmitter Running!')
    Transmitter().start_connection()


if __name__ == "__main__":
    main()