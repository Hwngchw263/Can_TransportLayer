import can
from enum import Enum, auto
from Std_Types import Std_ReturnType
from ComStack_Types import PduIdType, PduInfoType, BufReq_ReturnType
from PduRouter import PduR, pdur
from Can_If import CanIf, canif
import time
CANTP_OFF = 0
CANTP_ON = 1

class CanTp_RequestFrameType():
    SF_TX_REQUEST = 0
    MT_TX_REQUEST = 1

class CanTp_ConfigType:
    def __init__(self,
                 main_function_period: int,
                 FS:int,
                #  STmin: Separation Time (STmin)
                 STmin: int,
                #  BS: Block size
                 BS: int, 
                 addressing_format: str,
                 max_SF_DL: int,
                 max_FF_DL: int,
                 tx_data_buffer_size: int,
                 rx_data_buffer_size: int
                ):
                 
        # """
        # Initialize the CAN TP configuration structure
        # :param main_function_period: Period for calling the CAN TP main function (in milliseconds).
        # :param STmin: Minimum separation time between consecutive frames (in milliseconds).
        # :param BS: Block size (number of frames before sending flow control).
        # :param addressing_format: CAN addressing format ('STANDARD' or 'EXTENDED').
        # :param max_SF_DL: Maximum single frame data length.
        # :param max_FF_DL: Maximum first frame data length.
        # :param tx_data_buffer_size: Transmission buffer size.
        # :param rx_data_buffer_size: Reception buffer size.
        # """
        self.main_function_period = main_function_period
        # Flow Control Frame fields
        self.FS = FS
        self.STmin = STmin
        self.BS = BS
        self.addressing_format = addressing_format
        self.max_SF_DL = max_SF_DL
        self.max_FF_DL = max_FF_DL
        self.tx_data_buffer_size = tx_data_buffer_size
        self.rx_data_buffer_size = rx_data_buffer_size

class CanTp:
    # After power up
    MAX_SINGLE_FRAME_LENGTH = 8 # Maximum length for a Single Frame N-PDU
    MAX_FRAME_LENGTH = 4095        # Example maximum length for a Multi-Frame N-PDU
    def __init__(self):
        self.CanTp_State = CANTP_OFF
        self.RequestFrameType = [0]
        # self.pdur = PduR()
        # self.canif = CanIf()
        self.canif = canif
        self.pdur = pdur
        self.CanTp_CfgPtr = None
        self.result = Std_ReturnType.E_NOT_OK

        self.received_data = []  # List để lưu trữ dữ liệu đã nhận
        self.total_length = None  # Tổng chiều dài dữ liệu
        self.received_length = 0  # Chiều dài dữ liệu đã nhận
        self.cf_count = 0  # Đếm số lượng Consecutive Frames đã nhận
        self.TpSduLength = 0

    def CanTp_Init(self, config: CanTp_ConfigType):
        self.CanTp_CfgPtr = config
        # """Initializes the CAN interface and sets the state to CANTP_ON (idle but ready)."""

        try:
            # self.bus = can.Bus(interface='neovi', channel=config.channel, bitrate=config.bitrate)
            self.CanTp_State = CANTP_ON  # Set state to CANTP_ON (idle, ready to transmit or receive)
            print("CanTp: CANTP initialized and set to CANTP_ON (idle)")
        except Exception as e:
            print(f"CanTp: Failed to initialize CANTP: {e}")
            self.CanTp_State = CANTP_OFF  # If there's an error, keep the state OFF
    # def CanTp_Shutdown(self):
    #     self.CanTp_State = CANTP_OFF  # Set state to CANTP_OFF
    
    def CanTp_Transmit(self, TxPduId: PduIdType, PduInfoPtr: PduInfoType):
        
        # """
        # Transmit the PDU with the specified ID and information.
        
        # :param TxPduId: The ID of the PDU to transmit (of type PduIdType).
        # :param PduInfoPtr: The information of the PDU to transmit (of type PduInfoType).
        # """
        ret = Std_ReturnType.E_OK
        # Step 1: Validate input parameters based on length only
        if PduInfoPtr.SduLength == 0 or PduInfoPtr.SduLength > self.MAX_FRAME_LENGTH:
            print("Error: Invalid PDU length.")
            ret = Std_ReturnType.E_NOT_OK

        # Step 2: Searches out the useful information to process the transmit request in the configuration set of this CanTp entity
        if PduInfoPtr.SduLength <= self.MAX_SINGLE_FRAME_LENGTH:
            # Simulate the transmission of a Single Frame N-PDU
            print("CanTp: Single frame transmission session.")
            self.RequestFrameType = CanTp_RequestFrameType.SF_TX_REQUEST
        else:
            # Initiate multi-frame transmission session
            print("CanTp: Multi frame transmission session.")
            self.RequestFrameType = CanTp_RequestFrameType.MT_TX_REQUEST

        #  Step 3: Launches an internal Tx task with parameters: TxPduId and PduInfoPtr
        # Tx_task(TxPduId, PduInfoPtr)
        return ret

    def CanTp_TxConfirmation(self, TxPduId: PduIdType, result: Std_ReturnType):
        if result == Std_ReturnType.E_NOT_OK:
            print("CanTp: Transmission of the PDU failed.")
        else:
            print("CanTp: The PDU was transmitted.")

    def Tx_task(self, TxPduId: PduIdType, PduInfoPtr: PduInfoType):
        print("CanTp: Active transmission task.")
        result = Std_ReturnType.E_NOT_OK
        if self.RequestFrameType == CanTp_RequestFrameType.SF_TX_REQUEST:
            result = self.send_single_frame(TxPduId, PduInfoPtr)
        else:
            self.send_first_frame(TxPduId, PduInfoPtr)
            try : 
                # Wait for the first FlowControl message containing BS and STmin.
                self.receive_flow_control()
                # Once flow control is received, start sending consecutive frames
                result = self.send_consecutive_frames(TxPduId, PduInfoPtr)
            except TimeoutError as e:
                print(e)
        self.pdur.PduR_CanTpTxConfirmation(PduIdType, result)

    def send_single_frame(self, TxPduId: PduIdType, PduInfoPtr: PduInfoType):
            print(f"CanTp: Sending single frame.")
            SF_DL = PduInfoPtr.SduLength
            Single_Frame = [0x00 | SF_DL] + PduInfoPtr.SduDataPtr
            if len(Single_Frame) < 8:
                Single_Frame += [0x00] * (8 - len(Single_Frame))  # Padding
            PDU = PduInfoType(SduDataPtr = Single_Frame, SduLength = len(Single_Frame))
            result = self.canif.CanIf_Transmit (TxPduId, PDU)
            self.CanTp_TxConfirmation(TxPduId, result)
            return result

    def send_first_frame(self, TxPduId: PduIdType, PduInfoPtr: PduInfoType):
            print(f"CanTp: Sending multi frames.")
            Pdu_Payload_length = PduInfoPtr.SduLength
            First_Frame = [0x10 | ((Pdu_Payload_length >> 8) & 0x0F), Pdu_Payload_length & 0xFF]
            First_Frame += PduInfoPtr.SduDataPtr[:6]  # First 6 bytes
            First_Frame += [0x00] * (8 - len(First_Frame))  # Padding
            print(f"Sending First Frame: {First_Frame}")
            PDU = PduInfoType(SduDataPtr = First_Frame, SduLength = len(First_Frame))
            result = self.canif.CanIf_Transmit (TxPduId, PDU)

    def send_consecutive_frames(self, TxPduId: PduIdType, PduInfoPtr: PduInfoType):
        sn = 1  # Sequence Number
        num_cf_sent = 0  # Track how many CFs have been sent
        time.sleep(0.1)
        for i in range(6, PduInfoPtr.SduLength, 7):
            if num_cf_sent == self.CanTp_CfgPtr.BS:
                # Block size reached, wait for next FlowControl
                print(f"Waiting for next FlowControl after sending {self.CanTp_CfgPtr.BS} CFs")
                self.receive_flow_control()
                num_cf_sent = 0  # Reset counter for the next block

            Consecutive_Frame = [0x20 | (sn & 0x0F)] + PduInfoPtr.SduDataPtr[i:i + 7]
            Consecutive_Frame += [0x00] * (8 - len(Consecutive_Frame))  # Padding
            print(f"Sending Consecutive Frame {sn}: {Consecutive_Frame}")
            PDU = PduInfoType(SduDataPtr = Consecutive_Frame, SduLength = len(Consecutive_Frame))
            result = self.canif.CanIf_Transmit (TxPduId, PDU)
            time.sleep(0.1)  # Apply STmin delay (convert ms to seconds)
            
            sn += 1
            num_cf_sent += 1

            if sn > 15:
                sn = 0
            self.CanTp_TxConfirmation(TxPduId, result)
        return result

    def reset_receiver(self):
        self.received_data = []
        self.total_length = None
        self.received_length = 0
        self.cf_count = 0
        
    def receive_flow_control(self):
        # Receive FlowControl frame containing FS, BS and STmin.
        Flow_Control_Frame = can.Message()
        start_time = time.time()
        while True:
            # Flow_Control_Frame = self.canif.CanTp_Receive()
            self.canif.CanIf_Receive(Flow_Control_Frame)
            # print(f"Received Flow Controll frame: {Flow_Control_Frame}")
            elapsed_time = time.time() - start_time
            if Flow_Control_Frame and Flow_Control_Frame.arbitration_id == 0x789:  # Example FC arbitration ID
                data = Flow_Control_Frame.data
                # Check if it's a FlowControl frame (PCI type = 0x3)
                if data[0] >> 4 == 0x3:  
                    self.CanTp_CfgPtr.FS = data[0]&0x8   #Flow Status
                    self.CanTp_CfgPtr.BS = data[1]       # Block Size
                    self.CanTp_CfgPtr.STmin = data[2]    # STmin
                    print(f"Received Flow Control: BS={self.CanTp_CfgPtr.BS}")
                    break
            # Notify the user every second about the waiting status
            if elapsed_time % 1 < 0.1:  # Check every second
                print(f"Waiting for Flow Control... {int(elapsed_time)} seconds elapsed")
        
        # Check if the timeout has been reached timeout = N_As + N_Bs
            if elapsed_time > 5:
                print("Timeout: No Flow Control received. Ending data transmission.")
                raise TimeoutError("Flow Control not received within 5 seconds.") 
            time.sleep(0.2) 

    def send_flow_control(self):
            # Flow Control Frame với PCI type là 0x30 (Flow Control), BS và STmin
            TxPduId =0x789
            PduInfoPtr = PduInfoType(SduDataPtr=[0x30|self.CanTp_CfgPtr.FS, self.CanTp_CfgPtr.BS, self.CanTp_CfgPtr.STmin, 0, 0, 0, 0, 0], SduLength = 8)
            try:
                print(f"Sending Flow Control Frame : ID={hex(TxPduId)}, Data={PduInfoPtr.SduDataPtr}")
                result = self.canif.CanIf_Transmit (TxPduId, PduInfoPtr)
            except can.CanError:
                print("Failed to send flow control frame")

    def combine_data(self):
        recv_msg = can.Message()
        # Receive data 
        try: 
            if self.canif.CanIf_Receive(recv_msg) == Std_ReturnType.E_OK:
                arbitration_id = hex(recv_msg.arbitration_id)
                # Ignore Flow Control messages with arbitration ID 0x789 (or whatever ID you use)
                if recv_msg.arbitration_id == 0x789:
                    #print("Ignoring Flow Control message")
                    return None  # Skip this messag
                data = recv_msg.data
                print(f"Received message: ID={arbitration_id}, Data={data}")
                
                # Kiểm tra loại frame dựa trên byte đầu tiên (PCI Type)
                PCI_type = data[0] >> 4  # PCI type là 4 bit cao của byte đầu tiên
                
                byte_2 = data[1]
                if PCI_type == 0x0:
                    # Single Frame (PCI type = 0x0)
                    print("Received a Single Frame, no flow control sent.")
                    SF_DL = data[0] & 0x0F  
                    self.received_data += list(data[1:1+SF_DL])  # Lưu dữ liệu từ Single Frame
                    
                    print(f"Data received: {self.received_data}")
                    self.reset_receiver()
                elif PCI_type == 0x1 and byte_2 !=0 :
                    # First Frame (PCI type = 0x1)
                    print("Received a First Frame, sending Flow Control Frame.")
                    FF_DL = ((data[0] & 0x0F) << 8) + data[1]  # Lấy FF_DL (12 bit)
                    self.total_length = FF_DL  # Tổng chiều dài dữ liệu
                    self.received_data += list(data[2:])  # Lưu 6 byte từ First Frame
                    self.received_length = len(self.received_data)
                    self.cf_count = 0  # Đặt lại bộ đếm Consecutive Frames
                    self.send_flow_control()  # Gửi Flow Control với BS = 4, STmin = 0
                elif PCI_type == 0x1 and byte_2 == 0 :
                    # First Frame (PCI type = 0x1)
                    print("Received a First Frame >4095, sending Flow Control Frame.")
                    FF_DL = (data[2] << 24) | (data[3] << 16) | (data[4] << 8) | data[5]
                    self.total_length = FF_DL  # Tổng chiều dài dữ liệu
                    self.received_data += list(data[6:])  # Lưu 2 byte từ First Frame
                    self.received_length = len(self.received_data)
                    self.cf_count = 0  # Đặt lại bộ đếm Consecutive Frames
                    self.send_flow_control()  # Gửi Flow Control với BS = 4, STmin = 0  
                elif PCI_type == 0x2:
                    # Consecutive Frame (PCI type = 0x2)
                    sn = data[0] & 0x0F  # Sequence Number (4 bit thấp)
                    print(f"Received a Consecutive Frame, SN={sn}")

                    self.received_data += list(data[1:])  # Lưu dữ liệu từ Consecutive Frame
                    self.received_length = len(self.received_data)
                    self.cf_count += 1  # Tăng bộ đếm CF

                    # Kiểm tra nếu đã nhận đủ toàn bộ dữ liệu
                    if self.received_length >= self.total_length:
                        time.sleep(2)
                        print(f"All data received: {self.received_data[0:self.total_length]}")
                        self.reset_receiver()
                    
                    # Nếu đã nhận đủ số lượng CF theo Block Size (BS)
                    if self.cf_count >= self.CanTp_CfgPtr.BS:
                        print(f"Received {self.CanTp_CfgPtr.BS} Consecutive Frames, sending new Flow Control.")
                        self.send_flow_control()  # Gửi Flow Control mới
                        self.cf_count = 0  # Đặt lại bộ đếm CF
                else:
                    print(f"Received another frame type: PCI type {PCI_type}")
                
                return recv_msg
            else:
                return None
        except Exception as e:
            print(f"CanTp: An error occurred: {e}")
            return None
        
    # def receive_data(self):
    #     recv_msg = can.Message()
    #     # Receive data 
    #     try: 
    #         if self.canif.CanIf_Receive(recv_msg) == Std_ReturnType.E_OK:
    #             # Information of I-PDu
    #             id =hex(recv_msg.arbitration_id)
    #             # Ignore Flow Control messages with arbitration ID 0x789 (or whatever ID you use)
    #             if id == 0x789:
    #                 #print("Ignoring Flow Control message")
    #                 return None  # Skip this messag
    #             info = PduInfoType(SduDataPtr=recv_msg.data, SduLength = len(recv_msg.data))
    #             print(f"Received message: ID={id}, Data={data}")
    #             # Check Type of Frame SF, FF, CF, FC
    #             data = recv_msg.data
    #             PCI_type = data[0] >> 4  # PCI type is 4 bit MSB of first byte
    #             byte_2 = data[1]
    #             # Single Frame
    #             if PCI_type == 0x0:
    #                 self.TpSduLength = data[0] & 0x0F
    #                 print(f"Received a Single Frame: {info.SduDataPtr}")
    #                 Copied_Data = recv_msg.data[1:]
    #                 info = PduInfoType(SduDataPtr=Copied_Data, SduLength = len(Copied_Data))
    #                 if self.pdur.PduR_CanTpStartOfReception(id, info,self.TpSduLength, self.pdur.bufferSizePtr) == BufReq_ReturnType.BUFREQ_OK:
    #                     if self.pdur.PduR_CanTpCopyRxData(id, info, self.pdur.bufferSizePtr) == BufReq_ReturnType.BUFREQ_OK:
    #                         self.received_length += info.SduLength
    #                         result = Std_ReturnType.E_OK
    #                         self.pdur.PduR_CanTpRxConfirmation(id, result)
    #                     else:
    #                         return None
    #                 else:
    #                     return None   
    #             # Multi Frame  
    #             #First Frame
    #             elif PCI_type == 0x1: 
    #                 if byte_2 !=0 :
    #                     self.TpSduLength = ((data[0] & 0x0F) << 8) + data[1]
    #                     Copied_Data = recv_msg.data[2:]
    #                     info = PduInfoType(SduDataPtr=Copied_Data, SduLength = len(Copied_Data))
    #                 else:
    #                     self.TpSduLength = (data[2] << 24) | (data[3] << 16) | (data[4] << 8) | data[5]
    #                     Copied_Data = recv_msg.data[6:]
    #                     info = PduInfoType(SduDataPtr=Copied_Data, SduLength = len(Copied_Data))
    #                 print(f"Received a First Frame: {info.SduDataPtr}")
    #                 result = self.pdur.PduR_CanTpStartOfReception(id, info,self.TpSduLength, self.pdur.bufferSizePtr)
    #                 if result == BufReq_ReturnType.BUFREQ_OK:
    #                     if self.pdur.PduR_CanTpCopyRxData(id, info, self.pdur.bufferSizePtr) == BufReq_ReturnType.BUFREQ_OK:
    #                         self.received_length += info.SduLength
    #                         result = Std_ReturnType.E_OK
    #                         self.pdur.PduR_CanTpRxConfirmation(id, result)
    #                     else:
    #                         return None
    #                 elif result == BufReq_ReturnType.BUFREQ_E_OVFL:
    #                     # Send Overflow FC
    #                     self.FS = 0x2
    #                     self.send_flow_control()
    #                     return None
    #                 else:
    #                     return None 
    #             # Consecutive Frame  
    #             elif PCI_type == 0x2:
    #                 SN = data[0] & 0x0F  # Sequence Number (4 LSB bits)
    #                 print(f"Received a Consecutive Frame: {info.SduDataPtr} , SN={SN}") 
    #                 if self.pdur.PduR_CanTpCopyRxData(id, info, self.pdur.bufferSizePtr) == BufReq_ReturnType.BUFREQ_OK:
    #                     self.cf_count += 1
    #                     self.received_length += info.SduLength
    #                     self.FS = 0x0
    #                     # Send Continue to send FC
    #                     self.send_flow_control()
    #                 else:
    #                     # Rx Buffer is full
    #                     # Empty_list = []
    #                     # info = PduInfoType(SduDataPtr = Empty_list , SduLength = 0)
    #                     # self.pdur.PduR_CanTpCopyRxData(id, info, self.pdur.bufferSizePtr)
    #                     # Send Wait FC 
    #                     self.FS = 0x1
    #                     self.send_flow_control()
    #                     # Simulation for waiting buffer available
    #                     time.sleep(1)
    #                     # Clear to send
    #                     self.FS = 0x0
    #                     self.send_flow_control()
    #                 # Check Data receive full
    #                 if self.received_length >= self.TpSduLength:
    #                     time.sleep(2)
    #                     print(f"All data received: {self.pdur.Rx_buffer[0:self.TpSduLength]}")
    #                     self.reset_receiver()
                    
    #                 # if received enough CF in Block Size (BS)
    #                 if self.cf_count >= self.CanTp_CfgPtr.BS:
    #                     print(f"Received {self.CanTp_CfgPtr.BS} Consecutive Frames, sending new Flow Control.")
    #                     self.FS = 0x0
    #                     # Send Continue to send FC
    #                     self.send_flow_control()  
    #                     self.cf_count = 0  
    #             elif PCI_type == 0x3:
    #                     print(f"Received a Flow Control Frame: {info.SduDataPtr}")
    #                     return None
    #             else:
    #                     print(f"Received another frame type: PCI type {PCI_type}")
    #                     return None
    #             return recv_msg
    #         else:
    #             return None
    #     except Exception as e:
    #         print(f"CanTp: An error occurred: {e}")
    #         return None

    def CanTp_RxIndication(self, RxPduId: PduIdType, PduInfoPtr: PduInfoType):

        pass

cantp = CanTp()