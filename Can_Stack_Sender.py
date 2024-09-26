from Std_Types import Std_ReturnType
from ComStack_Types import  PduInfoType, RetryInfoType, BufReq_ReturnType
from Can_Tp import  CanTp, CanTp_ConfigType, cantp 
from Can_If import CanIf, Can_ConfigType, canif
from PduRouter import PduR, pdur 
import random
# Example configuration setup for CanTp_ConfigType
CanTp_CfgPtr = CanTp_ConfigType(
    main_function_period=10,  # 10 ms main function period
    FS = 0,
    STmin=1,                # 50 ms minimum separation time
    BS = 2,                     # Block size of 8 frames
    addressing_format="STANDARD",  # Standard CAN addressing
    max_SF_DL=8,              # Max single frame data length (7 bytes)
    max_FF_DL=4095,             # Max first frame data length (12 bytes)
)

CanIf_CfgPtr= Can_ConfigType(
    channel=1,               # CAN channel 1
    interface='neovi',           # Standard CAN bus
    bitrate=1000000,             # 500 kbps CAN bitrate
)
Tx_buffer = []
Rx_buffer = []
# Alsway Null thus not mechanism
retry = RetryInfoType(
    TpDataState = 0,
    TxTpDataCnt = 0,
)
availableDataPtr = [0]

if __name__ == "__main__":
    try:
        # Transmit_SF_N_SDU(CanTp_CfgPtr,txpduid,pduinfo,RequestFrameType)
        while True:
            input_string = input("Enter your data (Press Enter to exit): ")
            if input_string == "":
                print("Exit.")
                break
            # x = 25 # Example: number of elements
            # data= [random.randint(0x00, 0xFF) for _ in range(x)]
            data = list(input_string.encode('utf-8'))
            # Create a PduInfoType with a small data payload (that fits in a single frame)
            pduinfo = PduInfoType(SduDataPtr=data, SduLength = len(data))
            txpduid = 0x123  # Example PDU ID  
            pdur.PduR_Init(txpduid, pduinfo)
            cantp.CanTp_Init(CanTp_CfgPtr)
            canif.CanIf_Init(CanIf_CfgPtr)
            result = cantp.CanTp_Transmit(txpduid,pduinfo)
            if  result == Std_ReturnType.E_OK :
                # Lock Tx_buffer prevent upper layer writing data inside
                print("CanTp: Transmit request has been accepted.")
                cantp.Transmit_data(txpduid, pduinfo)
            else:
                print("CanTp: Transmit request has been accepted.")  
    except KeyboardInterrupt:
        print("Process interrupted")