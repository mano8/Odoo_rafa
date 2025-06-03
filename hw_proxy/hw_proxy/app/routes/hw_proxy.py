"""
Api routes for hw_proxy module
"""
import logging
import asyncio
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from hw_proxy.tools.pos_helper import EscPosHelper
from hw_proxy.core.config import settings

logger = logging.getLogger("hw_proxy")

router = APIRouter()

IOT_BOX_SECRET = None
# --- Constantes ESC/POS legibles ---
CMD_CUT = b"\x1D\x56\x01"        # Corte completo
CMD_CASHDRAWER = b"\x1B\x70\x00\x19\xFA"  # Apertura de cajón


# --- Security Dependency ---
# , dependencies=[Depends(verify_secret)]
async def verify_secret(
    x_iot_box_secret: str = Header(
        ...,
        alias="X-IOT-BOX-SECRET"
    )
):
    if x_iot_box_secret != IOT_BOX_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: invalid IoT Box secret"
        )
    return True


@router.get("/hello")
async def hello():
    """Emulates IoT Box hello endpoint"""
    return "ping"


@router.post("/handshake")
async def handshake(body: dict):
    """Emula el handshake JSON-RPC del IoT Box"""
    # return True
    req_id = body.get("id")
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "supports": {
                "print": True,
                "cut": True,
                "cashdrawer": True
            },
            "version": "1.0"
        }
    }


@router.post("/customer_facing_display")
async def customer_facing_display(req: Request):
    """Custormer facing display used for client Pos Display"""
    body = await req.json()
    req_id = body.get("id")
    params = body.get("params", {})
    # Fake action: log or process display data
    logger.debug("[DISPLAY]", params)
    return {"jsonrpc": "2.0", "id": req_id, "result": {"success": True}}


@router.post("/status_json")
async def status_json(req: Request):
    """
    Get Hardware status.
    Only accept printer and cashdrawer.
    Exact expected output is not clear.
    """
    try:
        logger.debug(
            "[status_json] Get printer status "
            f"for device: {settings.PRINTER_KEY}"
        )
        pos = EscPosHelper(settings.PRINTER_KEY)
        # await asyncio.to_thread(pos.get_printer_status())
        status = pos.get_full_printer_status()
        logger.debug(
            f"[status_json] status: {status}"
        )
        current_status = pos.get_str_full_printer_status(
            printer_status=status
        )
        logger.debug(
            f"[status_json] current_status: {current_status}"
        )
        return JSONResponse({
            "jsonrpc": "2.0",
            # in case of global status is required
            "status": current_status,
            "scanner": {  # Possible: no utilities to work
                "status": "disconnected"
            },
            "printer": {  # Possible
                "status": current_status
            },
            "cashbox": {  # Unknown: Depends on printer
                "status": current_status
            },
            "cashdrawer": {  # Unknown: Depends on printer
                "status": current_status
            },
            "scale": {  # Possible: no utilities to work
                "status": "disconnected"
            },
            "customer_facing_display": {  # Possible: no utilities to work
                "status": "disconnected"
            },
            "customer_display": {  # Possible: no utilities to work
                "status": "disconnected"
            },
            "display": {  # Possible: no utilities to work
                "status": "disconnected"
            },
            "printer_detail": status
        })
    except Exception as e:
        logger.error(f"Error in status_json: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {e}"
        ) from e


@router.post("/default_printer_action")
async def default_printer_action(req: Request):
    """
    Handle generic default_printer_action calls from Odoo POS
    see odoo  /web/static/src/core/network/rpc.js
    For response format.
    """
    logger.debug("Start Default printer Action...")
    action = None
    try:
        body = await req.json()
        req_id = body.get("id")
        params = body.get("params", {})
        data = params.get("data", {})
        action = data.get("action")
        receipt = data.get("receipt")
        pos = EscPosHelper(settings.PRINTER_KEY)
        # asyncio.create_task(asyncio.to_thread(_job))
        result = pos.default_printer_action(
            action=action,
            receipt=receipt
        )
        if result:
            # Successful response
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"success": True}
                }
            )
        else:
            # Error response
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -1,
                        "message": "Unable to run printer action",
                        "data": {"action": action}
                    }
                }
            )

    except Exception as e:
        logger.error(f"Fatal Error: Unable to run printer action: {action}")
        logger.debug(f"Exception: {e}")

        # Error response for exceptions
        raise HTTPException(
            status_code=500,
            detail={
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -1,
                    "message": (
                        "Fatal Error: Unable to run printer "
                        f"action: {action}"
                    ),
                    "data": {"action": action}
                }
            }
        )


@router.post("/open_cashdrawer")
async def open_cashdrawer():
    """Open cash drawer without printing."""
    try:
        pos = EscPosHelper(settings.PRINTER_KEY)
        pos.open_cashdrawer()
    except Exception as e:
        logger.error("Unable to oppen cash drawer.")
        logger.debug(f"Exception: {e}")
        # Error response for exceptions
        raise HTTPException(
            status_code=500,
            detail="Unable to oppen cash drawer."
        )


@router.post("/cut")
async def cut_paper(printer_name: str):
    """Cut paper without printing."""
    async def _job():
        pos = EscPosHelper(settings.PRINTER_KEY)
        printer = pos.get_printer()
        await asyncio.to_thread(printer._raw, CMD_CUT)
    asyncio.create_task(_job())
    return {"success": True}
