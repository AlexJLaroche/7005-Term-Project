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
        self.net = (self.conf.net_address,self.conf.net_port)
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
        self.num_packets_sent=0
        self.num_packets_resent=0

    # ---Function: create_packet----
    # Returns a packet Object with the specific required entries
    def create_packet(self, packet_type,window_size,seq_num=None, ack_num=None, p_data=""):
        packet = packets.Packet(self.conf.transmit_address, self.conf.transmit_port, self.conf.receive_address, 
        self.conf.receive_port, packet_type, seq_num, p_data, window_size, ack_num)
        return packet


    # ---Function: transmit----
    # 1. While loops is created to loop through the provided data
    # 2. Buffer Sequence and Ack Numbers are set in case of Retransmission
    # 3. Fixes the length of the data to ensure it can full the current Window Size
    # 4. Loops through the current Window Size, and sends packets accordingly
    # 5. Sets A buffer for the Expected Ack
    # 6. Calls the Window Ack Function
    # 7. Empties the Sent Data Buffer
    # 8. Unless the Socket is an SOT, then increase the Window Size = Window Size * 2, 
    #    until it reaches the Window Size specified in the config
    def transmit(self,data,packet_type):
        e = 0
        while e < len(data):#1
            i=0
            self.tx_buffer_seq = self.seq_num #2
            self.tx_buffer_ack = self.ack_num
            while len(data[e+i:]) % self.window_size != 0: #3
                data.append('.')
            while i < self.window_size: #4
                self.send_data(data[e+i],packet_type)
                self.num_packets_sent+=1
                i += 1
            self.buffer_expected_ack = self.expected_ack.copy() #5
            self.window_ack()#6
            self.buffer_sender_data = [] #7
            
            if packet_type == "S": #8
                e+=1
            else:
                if self.window_size < self.conf.window_size:
                    self.window_size = self.window_size * 2
                else:
                    self.window_size = self.conf.window_size
                e = e + self.window_size
            
            

    # ---Function: send_data----
    # 1. Create an PUSH ACK packet ("P.") using the provided data, 
    #    and send the packet to the network emulator. 
    # 2. Setting the Sequence Number to Sequence Number + the length of the Packet Data
    # 3. Appends the PUSH ACK to the Buffer List used for Retransmittion 
    def send_data(self, data, packet_type):
        packet_PSH_ACK = self.create_packet(packet_type, self.window_size, seq_num=self.seq_num, ack_num=self.ack_num, p_data=data) #1
        print(UDP.format_packet(packet_PSH_ACK))
        logging.info(UDP.format_packet(packet_PSH_ACK))
        UDP.send_packet(self.socket, packet_PSH_ACK, self.net)

        self.seq_num = self.seq_num + len(packet_PSH_ACK.data) #2
        self.buffer_sender_data.append(packet_PSH_ACK) #3

        ack_num = packet_PSH_ACK.seq_num + len(packet_PSH_ACK.data)
        seq_num = packet_PSH_ACK.ack_num
        self.expected_ack.append(ack_num)


    # ---Function: receive_ack----
    # 1. Set a timeout for the socket's listening to indicate the need for a Retransmittion
    # 2. Receive ACK and set the Sequence Number and ACK Number.
    # 3. If the socket timeouts then set that the order is False and Retransmitting will begin
    def receive_ack(self):
        self.socket.settimeout(self.conf.timeout) #1
        try:
            receiver_res = UDP.get_packet(self.socket) #2
            packet_ACK = pickle.loads(receiver_res[0])
            print(UDP.format_packet(packet_ACK))
            logging.info(UDP.format_packet(packet_ACK))
            self.ack_num = packet_ACK.seq_num + len(packet_ACK.data)
            self.seq_num = packet_ACK.ack_num 
        except socket.timeout as e: #3
            self.order = False
            print("SOCKET TIMED OUT RETRANSIMTTING.....")
            logging.info('SOCKET TIMED OUT RETRANSIMTTING.....')
            
    # ---Function: receive_ack----
    # 1. Sets The Order to True
    # 2. Send the packets from the Saved Buffer
    def retransmit_packets(self):
        self.order = True #1
        logging.info('Retransmitting: ')
        self.num_packets_resent = self.num_packets_resent + len(self.buffer_sender_data)
        for i in self.buffer_sender_data: #2
            print('Retransmitting: ', end="")
            print(UDP.format_packet(i))
            logging.info(UDP.format_packet(i))
            UDP.send_packet(self.socket, i, self.net)

    # ---Function: window_ack----
    # 1. Receives ACKs based on the current Window Size
    # 2. If the order is broken then break out of the Loop
    #    set the Sequence Number and ACK to their tx buffer counterparts,
    #    copy the expected acks from the buffer.
    # 3. Call on the retransmit_packets function
    # 4. Recall the window_ack 
    def window_ack(self):
        o = 0
        while o < self.window_size: #1
            if self.order == False: #2
                break
            else:
                self.receive_ack() #1
            o += 1
        if self.order == False: #2
            self.seq_num = self.tx_buffer_seq
            self.ack_num = self.tx_buffer_ack
            self.expected_ack = self.buffer_expected_ack.copy()
            self.retransmit_packets() #3
            self.window_ack() #4

    # ---Function: split_data----
    # Splits data into the maximum packet size specified in the config
    def split_data(self,data):
        n = self.conf.max_packet_size
        list_data = [data[i:i+n] for i in range(0, len(data), n)]
        self.sep_data = list_data
    

    # ---Function: start_connection----
    # 1. Initializes a server and binds it to the network addess and port 
    #    specified in the configuration file.
    # 2. Sends an SOT to indicate that the transmitter will start sending Data
    # 3. While there is a connection, have the user input data to send, 
    #    call the function split_data on the Data Entered, and the call the function 
    #    transmit to transmit the data
    # 4. If a Keyboard Interupt Occurs, Transmit the EOT, Receive the ACK, then Exit the script
    def start_connection(self):
        self.socket = UDP.create_server(self.conf.transmit_address, self.conf.transmit_port) #1
        print("Starting Connection...")
        self.transmit(".", "S") #2     
        
        print("Connection Established...")
        connection = True
        while connection: #3
            try:
                enter_data =  input('Enter Data to Sender: ')
                self.split_data(enter_data)
                self.transmit(self.sep_data,"P.")
            except KeyboardInterrupt: #4
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