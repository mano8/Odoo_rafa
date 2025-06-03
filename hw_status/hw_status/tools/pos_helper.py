"""
escpos helper for hw_status module
"""
import logging
import base64
from typing import Literal, Optional, Union
from escpos.printer import Usb, Network, Serial, Dummy
from io import BytesIO
from PIL import Image
from hw_status.tools.device_helper import DeviceHelper
from hw_status.core.exceptions import HwDeviceError, HwPrinterError
from hw_status.core.schemas import DeviceConfigSchemas, NetworkDeviceSchemas, PrinteImageConfSchemas, SerialDeviceSchemas, UsbDeviceSchemas
from hw_status.core.supported_devices import DevicePortType, DeviceType, device_list


logger = logging.getLogger("hw_status")


CMD_CUT = b"\x1D\x56\x01"        # Corte completo
CMD_CASHDRAWER = b"\x1B\x70\x00\x19\xFA"  # Apertura de cajón


class EscPosHelper(DeviceHelper):
    """
    escpos helper for hw_status module
    """
    def __init__(self, device_key: str):
        DeviceHelper.__init__(self, device_key)
        self.device = self.select_device(device_key)
        self.printer = None

    def init_printer(self, printer_key: Optional[str] = None):
        """Get escpos printer object from printer configuration."""
        self.select_device(printer_key)

        if self.has_printer_conf() is False:
            raise HwDeviceError(
                "Fatal Error: Invalid device configuration. "
                "Your device must be present in supported_list items."
            )
        
        if self.device.type != DeviceType.PRINTER:
            raise HwDeviceError(
                "Fatal Error: Invalid device type. "
                "EscPosHelper is dedicated to escpos printers. "
                "Please choose a printer device."
            )

        try:
            ptype = self.device.port_type
            if ptype == DevicePortType.USB:
                self.printer = Usb(
                    self.device.vendor,
                    self.device.product,
                    in_ep=self.device.conf.in_ep,
                    out_ep=self.device.conf.out_ep
                )
            elif ptype == DevicePortType.NETWORK:
                self.printer = Network(
                    host=self.device.conf.host,
                    port=self.device.conf.port
                )
            elif ptype == DevicePortType.SERIAL:
                self.printer = Serial(
                    devfile=self.device.conf.devfile,
                    baudrate=self.device.conf.baudrate,
                    bytesize=self.device.conf.bytesize,
                    parity=self.device.conf.parity,
                    stopbits=self.device.conf.stopbits,
                    timeout=self.device.conf.timeout,
                    dsrdtr=self.device.conf.dsrdtr,
                    profile=self.device.conf.profile
                )
            else:
                raise HwPrinterError(
                    f"Unsupported printer port type: {ptype.value}"
                )
        except Exception as e:
            raise HwPrinterError(
                f"Fatal Error: Printer connection error: {e}"
            ) from e
        return self.printer

    def has_printer(self):
        """Test if escpos printer is initialized."""
        return isinstance(self.printer, (Usb, Network, Serial, Dummy))
    
    def is_printer_ready(self, initialized: bool = False):
        """Test if escpos printer is initialized."""
        return self.has_printer()\
            and self.get_bool_full_printer_status(initialized=initialized)

    def close_printer(self):
        """Close escpos printer."""
        result = False
        if isinstance(self.printer, Dummy):
            logger.debug(
                "[close_printer] Printer is a Dummy instance, "
                "no close action needed."
            )
            result = True
        elif self.has_printer():
            try:
                self.printer.close()
                self.printer = None
                result = True
            except Exception as e:
                logger.error(f"[close_printer] Error closing printer: {e}")
                raise HwPrinterError(
                    f"Fatal Error: Unable to close printer, error: {e}"
                ) from e
        return result       

    def get_printer_status(self, initialized: bool = False):
        """Get escpos printer status."""
        result = None
        try:
            if initialized is not True:
                self.init_printer()
            if self.has_printer():
                is_online = self.printer.is_online()
            else:
                result = {
                    "is_online": False
                }
        except Exception as e:
            logger.error(
                "[get_printer_status] Fatal Error: Unable to get printer status, "
                f"error: {e} "
            )
            result = {
                "is_online": False,
                "error": str(e)
            }
        finally:
            logger.debug(
                f"[get_printer_status] Printer status: {is_online}, "
            )
            if initialized is not True:
                self.close_printer()
        return result
    
    def get_paper_printer_status(self, initialized: bool = False):
        """Get escpos printer status."""
        result = None
        try:
            if initialized is not True:
                self.init_printer()
            if self.has_printer():
                paper_status_code = self.printer.paper_status()
                paper_status_map = {
                    2: "ok",
                    1: "near_end",
                    0: "no_paper"
                }
                paper_status = paper_status_map.get(paper_status_code, "unknown")
                result = {
                    "paper_status": paper_status
                }
            else:
                result = {
                    "paper_status": "unknown"
                }
        except Exception as e:
            logger.error(
                "[get_paper_printer_status] Fatal Error: Unable to get printer status, "
                f"error: {e} "
            )
            result = {
                "paper_status": "unknown",
                "error": str(e)
            }
        finally:
            logger.debug(
                f"[get_paper_printer_status] Printer paper status: {paper_status}, "
            )
            if initialized is not True:
                self.close_printer()
        return result

    def get_full_printer_status(self, initialized: bool = False):
        """Get escpos printer status."""
        result = None
        try:
            if initialized is not True:
                self.init_printer()
            if self.has_printer():
                is_online = self.printer.is_online()
                paper_status_code = self.printer.paper_status()
                paper_status_map = {
                    2: "ok",
                    1: "near_end",
                    0: "no_paper"
                }
                paper_status = paper_status_map.get(paper_status_code, "unknown")
                result = {
                    "is_online": is_online,
                    "paper_status": paper_status
                }
            else:
                result = {
                    "is_online": False,
                    "paper_status": "unknown"
                }
        except Exception as e:
            logger.error(
                "[get_full_printer_status] Fatal Error: Unable to get printer status, "
                f"error: {e} "
            )
            result = {
                "is_online": False,
                "paper_status": "unknown",
                "error": str(e)
            }
        finally:
            logger.debug(
                f"[get_full_printer_status] Printer status: {is_online}, "
                f"Paper status: {paper_status} "
            )
            if initialized is not True:
                self.close_printer()
        return result

    def get_bool_printer_status(
        self,
        printer_status: Optional[Union[dict, bool]] = False,
        initialized: bool = False
    ) -> bool:
        """Get Bolean representation of escpos printer status."""
        if printer_status is False:
            printer_status = self.get_printer_status(initialized=initialized)
        return isinstance(printer_status, dict)\
            and printer_status.get("is_online", False) is True
    
    def get_bool_paper_printer_status(
        self,
        printer_status: Optional[Union[dict, bool]] = False,
        initialized: bool = False
    ) -> bool:
        """Get Bolean representation of escpos printer status."""
        if printer_status is False:
            printer_status = self.get_paper_printer_status(initialized=initialized)
        return isinstance(printer_status, dict)\
            and printer_status.get("paper_status", "unknown") == "ok"
    
    def get_bool_full_printer_status(
        self,
        printer_status: Optional[Union[dict, bool]] = False,
        initialized: bool = False
    ) -> bool:
        """Get Bolean representation of escpos printer status."""
        if printer_status is False:
            printer_status = self.get_full_printer_status(initialized=initialized)
        return isinstance(printer_status, dict)\
            and printer_status.get("is_online", False) is True\
            and printer_status.get("paper_status", "unknown") == "ok"

    def get_str_full_printer_status(
        self,
        printer_status: Optional[Union[dict, bool]] = False
    ) -> Literal["connected", "disconnected"]:
        """Get String representation of escpos printer status."""
        result = "disconnected"
        status = self.get_bool_full_printer_status(
            printer_status=printer_status
        )
        if status is True:
            result = "connected"
        return result

    def print_receipt(self, receipt: str):
        """Print receipt using escpos printer."""
        result = False
        try:
            self.init_printer()
            if self.is_printer_ready(initialized=True):
                logger.debug("[print_receipt] Convert receipt to Image...")
                img = self.format_base64_to_image(receipt)
                d = Dummy()
                d.image(img, impl="bitImageColumn")
                d.cut(feed=True)
                self.printer._raw(d.output)
                result = True
                logger.debug("[print_receipt] Ticket Impress with success...")
            else:
                logger.error(
                    "[print_receipt] Printer not initialized or not available."
                )
        except Exception as e:
            logger.error(
                "[print_receipt] Fatal Error: Unable to print receipt, "
                f"error: {e} "
            )
            self.close_printer()
            raise HwPrinterError(
                "[print_receipt] Fatal Error: Unable to print receipt, "
                f"error: {e} "
            ) from e
        finally:
            self.close_printer()
        return result

    def cut_receipt(self):
        """Cut receipt using escpos printer."""
        result = False
        try:
            self.init_printer()
            if self.is_printer_ready(initialized=True):
                logger.debug("[cut_receipt] Cut Receipt...")
                self.printer.cut(feed=True)
                result = True
            else:
                logger.error(
                    "[cut_receipt] Printer not initialized or not available."
                )
        except Exception as e:
            logger.error(
                "[cut_receipt] Fatal Error: Unable to cut receipt, "
                f"error: {e} "
            )
            self.close_printer()
            raise HwPrinterError(
                "[cut_receipt] Fatal Error: Unable to cut receipt, "
                f"error: {e} "
            ) from e
        finally:
            self.close_printer()
        return result

    def open_cashdrawer(self):
        """Open cash drawer using escpos printer."""
        result = False
        try:
            self.init_printer()
            if self.has_printer():
                logger.debug("[open_cashdrawer] Open Cash Drawer...")
                # Assuming CMD_CASHDRAWER is defined in escpos library
                self.printer._raw(CMD_CASHDRAWER)
                result = True
            else:
                logger.error(
                    "[open_cashdrawer] Printer not initialized or not available."
                )
        except Exception as e:
            logger.error(
                "[open_cashdrawer] Fatal Error: Unable to open cash drawer, "
                f"error: {e} "
            )
            self.close_printer()
            raise HwPrinterError(
                "[open_cashdrawer] Fatal Error: Unable to open cash drawer, "
                f"error: {e} "
            ) from e
        finally:
            self.close_printer()
        return result

    def default_printer_action(
        self,
        action: str,
        receipt: Optional[str] = None
    ):
        """Run default printer action."""
        result = False
        try:
            if action == "print_receipt":
                result = self.print_receipt(
                    receipt=receipt
                )
            elif action == "cut_receipt":
                result = self.cut_receipt()
            elif action in ("cashbox", "cashdrawer"):
                result = self.open_cashdrawer()
            else:
                logger.warning(
                    "[default_printer_action] Unknown "
                    f"default_printer_action: {action}"
                )
                result = False
        except Exception as e:
            logger.error(
                "[default_printer_action] Fatal Error: "
                f"Unable to run printer action: {action}, "
                f"error: {e}"
            )
            raise HwPrinterError(
                "[default_printer_action] Fatal Error: "
                f"Unable to run printer action: {action}, "
                f"error: {e} "
            ) from e
        return result


    @staticmethod
    def set_device_port_schema(
        port_type: DevicePortType,
        config: dict
    ) -> Image:
        """Set Device Port Schema model"""
        if isinstance(config, dict):
            if port_type == DevicePortType.USB:
                return UsbDeviceSchemas(**config)
            
            if port_type == DevicePortType.NETWORK:
                return NetworkDeviceSchemas(**config)
            
            if port_type == DevicePortType.SERIAL:
                return SerialDeviceSchemas(**config)
        return None

    @staticmethod
    def format_base64_to_image(
        b64string: str
    ) -> Image:
        """
        Transform base64 string in Pillow Image object.
        1. Decodifica Base64 -> bytes
        2. Abre con Pillow -> Image
        3. printer.image() usa internamente Pillow para ESC/POS
        4. Opcional: corte y apertura de cajón
        """
        try:
            # 1. Quitar prefijos si existen y decodificar
            if "," in b64string:
                b64string = b64string.split(",", 1)[1]
            raw = base64.b64decode(b64string)

            # 2. Abrir imagen en memoria
            return Image.open(BytesIO(raw)).convert("RGB")
        except Exception as e:
            raise HwPrinterError(
                "Error: Unable to convert "
                "base64 string to Pilow Image Object. \n"
                f"error: {e}"
            ) from e
    
    @staticmethod
    def save_image(
        img: Image.Image,
        filename: str = "ticket.png"
    ) -> Image:
        """
        Guarda la imagen en el directorio actual con el nombre dado.
        El formato se deduce de la extensión (.png, .jpg, etc.).
        """
        try:
            path = f"/tmp/{filename}"
            img.save(f"/tmp/{filename}")
            print(f"[DEBUG] Imagen guardada en: {filename}")
        except Exception as e:
            raise HwPrinterError(
                "Error: Unable to save image on file. "
                "- File name: {filename} \n"
                f"error: {e}"
            ) from e