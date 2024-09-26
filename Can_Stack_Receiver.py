from Std_Types import Std_ReturnType
from ComStack_Types import  PduInfoType, RetryInfoType, BufReq_ReturnType
from Can_Tp import  CanTp, CanTp_ConfigType, cantp 
from Can_If import CanIf, Can_ConfigType, canif
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

if __name__ == "__main__":
    try:
        # pdur.PduR_Init(txpduid, pduinfo)
        cantp.CanTp_Init(CanTp_CfgPtr)
        canif.CanIf_Init(CanIf_CfgPtr)
        print("Waiting to receive messages...")
        while True:
            # new_msg = cantp.combine_data()
            new_msg = cantp.receive_data()
    except KeyboardInterrupt:
        print("Process interrupted")