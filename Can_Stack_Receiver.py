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
    STmin=0,                # 50 ms minimum separation time
    BS = 4,                     # Block size of 8 frames
    addressing_format="STANDARD",  # Standard CAN addressing
    max_SF_DL=7,              # Max single frame data length (7 bytes)
    max_FF_DL=12,             # Max first frame data length (12 bytes)
    tx_data_buffer_size=256,   # Transmission buffer size (in bytes)
    rx_data_buffer_size=256    # Reception buffer size (in bytes)
)

CanIf_CfgPtr= Can_ConfigType(
    channel= 1,               # CAN channel 1
    interface='neovi',           # Standard CAN bus
    bitrate=500000,             # 500 kbps CAN bitrate
)
Tx_buffer = []
Rx_buffer = []
# Alsway Null thus not mechanism
retry = RetryInfoType(
    TpDataState = 0,
    TxTpDataCnt = 0,
)
availableDataPtr = [0]

x = 10 # Example: number of elements
data= [random.randint(0x00, 0xFF) for _ in range(x)]
# Create a PduInfoType with a small data payload (that fits in a single frame)
pduinfo = PduInfoType(SduDataPtr=data, SduLength = x)
txpduid = 0x01  # Example PDU ID

if __name__ == "__main__":
    try:
        # pdur.PduR_Init(txpduid, pduinfo)
        cantp.CanTp_Init(CanTp_CfgPtr)
        canif.CanIf_Init(CanIf_CfgPtr)
        print("Waiting to receive messages...")
        while True:
            new_msg = cantp.combine_data()
    except KeyboardInterrupt:
        print("Process interrupted")