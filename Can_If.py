from Std_Types import Std_ReturnType
from ComStack_Types import PduIdType, PduInfoType
import can
class Can_ConfigType:
    def __init__(self,
                 channel: int,
                 interface: str,
                 bitrate: int
                ):
        self.channel = channel
        self.interface = interface
        self.bitrate = bitrate
class CanIf:
    def __init__(self):
        self.bus = None
    def __del__(self):
        if self.bus:
            self.bus.shutdown()
    def CanIf_Init(self, CanIf_CfgPtr: Can_ConfigType):
        try:
            self.bus = can.Bus(channel=CanIf_CfgPtr.channel, interface=CanIf_CfgPtr.interface, bitrate=CanIf_CfgPtr.bitrate)
            print("CanIf: CANIF initialized.")
        except Exception as e:
            print(f"CanIf: Failed to initialize CANIF: {e}")    

    def CanIf_Transmit (self,TxPduId: PduIdType, PduInfoPtr: PduInfoType):
        if not self.bus:
            print(f"CanIf: CAN message NOT sent: {e}")
            return Std_ReturnType.E_NOT_OK
        else:
            can_msg = can.Message(arbitration_id=TxPduId, data= PduInfoPtr.SduDataPtr, is_extended_id=False)
            try:
                self.bus.send(can_msg)
                return Std_ReturnType.E_OK
            except can.CanError as e:
                print(f"CanIf: CAN message NOT sent: {e}")
                return Std_ReturnType.E_NOT_OK

    def CanIf_Receive (self,Frame):
        if not self.bus:
            # print(f"CanIf: CAN message NOT receive: {e}")
            return Std_ReturnType.E_NOT_OK
        else:
            try:
                recv_msg = self.bus.recv(timeout = 1)
                if recv_msg:
                    # Update the attributes of Frame (assuming Frame is a can.Message object)
                    Frame.arbitration_id = recv_msg.arbitration_id
                    Frame.dlc = recv_msg.dlc
                    Frame.data = recv_msg.data
                    Frame.is_extended_id = recv_msg.is_extended_id
                    return Std_ReturnType.E_OK
                else:
                    return Std_ReturnType.E_NOT_OK
            except can.CanError as e:
                print(f"CanIf: CAN message NOT receive: {e}")
                return Std_ReturnType.E_NOT_OK

canif = CanIf()