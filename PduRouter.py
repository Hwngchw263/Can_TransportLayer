from Std_Types import Std_ReturnType
from ComStack_Types import PduIdType, PduInfoType, RetryInfoType, PduLengthType, BufReq_ReturnType

class PduR:
 
    def __init__(self):
        self.AppLayer_buffer = []
        self.AppLayer_Buffer_CurrentPosition = 0
        self.RX_BUFFER_SIZE = 100
        self.TX_BUFFER_SIZE = 100
        self.Tx_Buffer_CurrentPosition = 0
        self.Rx_Buffer_CurrentPosition = 0
        self.Rx_buffer = []
        self.Tx_buffer = []
        self.bufferSizePtr = self.RX_BUFFER_SIZE

    def PduR_Init(self,id: PduIdType, info: PduInfoType):
        self.IPduSize = info.SduLength
        self.IPduDataPtr = info.SduDataPtr
        print(f"Sent message: ID={hex(id)}, Data={info.SduDataPtr}")

    # def PduR_CanTpCopyTxData(self,id: PduIdType, info: PduInfoType,retry: RetryInfoType, availableDataPtr: PduLengthType):
    #     # Parameters (in) id, info, retry
    #     # Parameters (out) availableDataPtr: remaining number of bytes that are available in the upper layer module’s Tx buffer
    #     # Take information of PDU from id
        
    #     if (self.CurrentPosition + info.SduLength) <= self.IPduSize:
    #         # Point to the correct position in the buffer
    #         source = self.IPduDataPtr[self.CurrentPosition:]
    #         # Lock transmit buffer

    #         # Assign the data pointer
    #         info.SduDataPtr = source
    #         # Update the buffer position
    #         self.CurrentPosition += info.SduLength
    #         # Calculate available data
    #         availableDataPtr[0] = self.IPduSize - self.CurrentPosition
    #         return BufReq_ReturnType.BUFREQ_OK
    #     # 
    #     else:
    #         return BufReq_ReturnType.BUFREQ_E_NOT_OK
    def PduR_CanTpCopyRxData(self,id: PduIdType, info: PduInfoType, bufferSizePtr: PduLengthType):
        ret = BufReq_ReturnType.BUFREQ_OK
        # Check available buffer to be copied
        if info.SduLength <= bufferSizePtr:
            # Save data to the buffer
            self.Rx_buffer += list(info.SduDataPtr[0:])
            # Update Rx_Buffer_CurrentPosition
            self.Rx_Buffer_CurrentPosition += info.SduLength
            # Monitor the remaning buffer size
            self.bufferSizePtr = bufferSizePtr - info.SduLength
        else:
            ret =  BufReq_ReturnType.BUFREQ_E_NOT_OK
        return ret
    def PduR_CanTpTxConfirmation(self, id: PduIdType, result: Std_ReturnType):
        if result == Std_ReturnType.E_NOT_OK:
            print("PduR: The transport transmission session is aborted.")
        else:
            print("PduR: The transport transmission session is successfully completed.")
            # Unlock Tx buffer for upper layer write data inside
    def PduR_CanTpRxConfirmation(self, id: PduIdType, result: Std_ReturnType):
        if result == Std_ReturnType.E_NOT_OK:
            print("PduR: Reception of the PDU failed.")
        else:
            print("PduR: The PDU was received.")
            # Unlock Rx buffer for upper layer write or read data inside
    def PduR_CanTpStartOfReception(self,id: PduIdType, info: PduInfoType, TpSduLength: PduLengthType , bufferSizePtr: PduLengthType):
        # Allocate Rx_buffer
        # No buffer of the required length can be provided
        ret = BufReq_ReturnType.BUFREQ_OK
        # if bufferSizePtr < TpSduLength:
        #     ret = BufReq_ReturnType.BUFREQ_E_OVFL
        # else:
        #     return BufReq_ReturnType.BUFREQ_OK
        # Lock Rx_buffer
        return ret

pdur = PduR()