"""
Device helper for hw_proxy module
"""
from typing import Optional
from hw_proxy.core.schemas import DeviceConfigSchemas, PrinteImageConfSchemas
from hw_proxy.core.supported_devices import device_list


class DeviceHelper:
    """
    Device helper for hw_proxy module
    """
    def __init__(self, device_key: str):
        self.device_key = None
        self.device = self.select_device(device_key)

    def select_device(self, device_key: str):
        """Select device in device_list"""
        for device in device_list:
            key = device.get("key", None)
            if key == device_key:
                image_conf = None
                if device.get('image_conf') is not None:
                    image_conf = PrinteImageConfSchemas(
                        **device.get('image_conf')
                    )
                return DeviceConfigSchemas(
                    vendor=device.get('vendor'),
                    product=device.get('product'),
                    name=device.get('name'),
                    key=device.get('key'),
                    type=device.get('type'),
                    port_type=device.get('port_type'),
                    conf=self.set_device_port_schema(
                        port_type=device.get('port_type'),
                        config=device.get('conf')),
                    image_conf=image_conf
                )
        return None

    def set_device_conf(
        self,
        device_key: Optional[str] = None
    ):
        """Set printer configuration."""
        if device_key is not None:
            self.device_key = device_key
            self.device = self.select_device(device_key)

    def has_printer_conf(self):
        """Has valid printer configuration"""
        return isinstance(self.device, DeviceConfigSchemas)
