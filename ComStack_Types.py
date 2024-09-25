from enum import Enum, auto
# Define BufReq_ReturnType as a simple class
class BufReq_ReturnType(Enum):
    BUFREQ_OK = auto()
    BUFREQ_E_NOT_OK = auto()
    BUFREQ_E_BUSY = auto()
    BUFREQ_E_OVFL= auto()
# Define PduId as a simple class
class PduIdType:
    def __init__(self, PduId: int):
        self.PduId = PduId
# Define PduLengthType as a simple class
class PduLengthType:
    def __init__(self, PduLength: int):
        self.PduLength = PduLength
class PduBufferStateType:
    def __init__(self, CurrentPosition: PduLengthType):
        self.CurrentPosition = CurrentPosition
# Define PduInfoType as a simple class
class PduInfoType:
    def __init__(self, SduLength, SduDataPtr):
        self.SduLength = SduLength
        self.SduDataPtr = SduDataPtr  # Initialize SduDataPtr
        # Meta data
        self.MetaDataPtr = None
# Define TPParameterType as a simple class
class TPParameterType(Enum):
    TP_STMIN = auto()
    TP_BS = auto()
    TP_BC = auto()
# Define TpDataStateType as a simple class
class TpDataStateType(Enum):
    TP_DATACONF = auto()
    TP_DATARETRY= auto()
    TP_CONFPENDING = auto()
# Define RetryInfoType as a simple class
class RetryInfoType:
    def __init__(self, TpDataState: TpDataStateType, TxTpDataCnt: PduLengthType ):
        self.TpDataState = TpDataState
        self.TxTpDataCnt = TxTpDataCnt
