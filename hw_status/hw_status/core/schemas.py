"""
Pydantic schemas for hw_status module
"""


from typing import Literal, Optional, Union
from pydantic import BaseModel

from hw_status.core.supported_devices import DevicePortType, DeviceType


class UsbDeviceSchemas(BaseModel):
    """Device pydantic Schemas"""
    in_ep: int
    out_ep: int

class NetworkDeviceSchemas(BaseModel):
    """Device pydantic Schemas"""
    host: str
    port: int = 9100

class SerialDeviceSchemas(BaseModel):
    """Device pydantic Schemas"""
    devfile: str
    baudrate: int
    bytesize: Optional[int] = None
    parity: Optional[Literal['Y', 'N']] = None
    stopbits: Optional[int] = None
    timeout: Union[int, float]
    dsrdtr: Optional[bool] = None
    profile: Optional[str] = None


class PrinteImageConfSchemas(BaseModel):
    """Device pydantic Schemas"""
    impl: Literal["bitImageColumn", "Image"]


class DeviceConfigSchemas(BaseModel):
    """Device pydantic Schemas"""
    vendor: str
    product: str
    name: str
    key: str
    type: DeviceType
    port_type: DevicePortType
    conf: Union[
        UsbDeviceSchemas,
        NetworkDeviceSchemas,
        SerialDeviceSchemas
    ]
    image_conf: Optional[PrinteImageConfSchemas] = None


class PrintRequest(BaseModel):
    printer_name: str
    data: str              # base64-encoded ESC/POS bytes
    cut: bool = True
    cashdrawer: bool = False