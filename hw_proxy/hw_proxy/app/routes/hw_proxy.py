"""
Api routes for hw_proxy module
"""
import logging
import time
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from hw_proxy.core.deps import get_printer_pool
from hw_proxy.core.printer_pool import PrinterPool
from hw_proxy.schemas.receipt import PrintReceiptJsonRequest
from hw_proxy.metrics import (
    cashdrawer_operations_total,
    print_duration_seconds,
    print_jobs_total,
    printer_online,
    printer_paper_ok,
)

logger = logging.getLogger("hw_proxy")

router = APIRouter()

IOT_BOX_SECRET = None


async def verify_secret(
    x_iot_box_secret: str = Header(..., alias="X-IOT-BOX-SECRET")
):
    if x_iot_box_secret != IOT_BOX_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: invalid IoT Box secret")
    return True


@router.get("/hello")
async def hello():
    """Emulates IoT Box hello endpoint."""
    return "ping"


@router.post("/handshake")
async def handshake(body: dict):
    """Emulates IoT Box handshake JSON-RPC endpoint."""
    return {
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "result": {
            "supports": {"print": True, "cut": True, "cashdrawer": True},
            "version": "1.0",
        },
    }


@router.post("/customer_facing_display")
async def customer_facing_display(req: Request):
    """Customer-facing display stub."""
    body = await req.json()
    logger.debug("[DISPLAY] %s", body.get("params", {}))
    return {"jsonrpc": "2.0", "id": body.get("id"), "result": {"success": True}}


@router.post("/status_json")
async def status_json(
    pool: PrinterPool = Depends(get_printer_pool),
):
    """Return hardware status — used by Odoo POS to check connectivity."""
    try:
        logger.debug("[status_json] querying printer via pool")
        status = await pool.get_full_status()

        printer_online.set(1 if status.get("is_online") else 0)
        printer_paper_ok.set(1 if status.get("paper_status") == "ok" else 0)

        is_ok = status.get("is_online") and status.get("paper_status") == "ok"
        current_status = "connected" if is_ok else "disconnected"

        return JSONResponse({
            "jsonrpc": "2.0",
            "status": current_status,
            "scanner": {"status": "disconnected"},
            "printer": {"status": current_status},
            "cashbox": {"status": current_status},
            "cashdrawer": {"status": current_status},
            "scale": {"status": "disconnected"},
            "customer_facing_display": {"status": "disconnected"},
            "customer_display": {"status": "disconnected"},
            "display": {"status": "disconnected"},
            "printer_detail": status,
        })
    except Exception as e:
        logger.error("[status_json] error: %s", e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}") from e


@router.post("/default_printer_action")
async def default_printer_action(
    req: Request,
    pool: PrinterPool = Depends(get_printer_pool),
):
    """Handle print/cut/cashdrawer actions from Odoo POS."""
    body = await req.json()
    action = None
    try:
        req_id = body.get("id")
        params = body.get("params", {})
        data = params.get("data", {})
        action = data.get("action")
        receipt = data.get("receipt")

        _t0 = time.perf_counter()
        result = await pool.default_action(action=action, receipt=receipt)
        _dur = time.perf_counter() - _t0
        _label = "success" if result else "error"
        print_duration_seconds.labels(action=action or "unknown").observe(_dur)
        print_jobs_total.labels(action=action or "unknown", result=_label).inc()

        if result:
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"success": True}})
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -1, "message": "Unable to run printer action", "data": {"action": action}},
        })

    except Exception as e:
        logger.error("[default_printer_action] fatal: action=%s error=%s", action, e)
        raise HTTPException(
            status_code=500,
            detail={
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -1,
                    "message": f"Fatal Error: Unable to run printer action: {action}",
                    "data": {"action": action},
                },
            },
        ) from e


@router.post("/open_cashdrawer")
async def open_cashdrawer(pool: PrinterPool = Depends(get_printer_pool)):
    """Open cash drawer without printing."""
    try:
        await pool.open_cashdrawer()
        cashdrawer_operations_total.labels(result="success").inc()
        return {"success": True}
    except Exception as e:
        cashdrawer_operations_total.labels(result="error").inc()
        logger.error("[open_cashdrawer] %s", e)
        raise HTTPException(status_code=500, detail="Unable to open cash drawer.") from e


@router.post("/cut")
async def cut_paper(pool: PrinterPool = Depends(get_printer_pool)):
    """Cut paper without printing."""
    try:
        await pool.cut()
        return {"success": True}
    except Exception as e:
        logger.error("[cut] %s", e)
        raise HTTPException(status_code=500, detail="Unable to cut paper.") from e


@router.post("/print_receipt_json")
async def print_receipt_json(
    data: PrintReceiptJsonRequest,
    pool: PrinterPool = Depends(get_printer_pool),
) -> JSONResponse:
    """
    Accept a structured receipt JSON and render to ESC/POS text commands.

    Payload is ~2-4 KB vs ~56 KB for a raster image, reducing serial write
    time from ~4.8 s to ~0.2 s at 115 200 baud.  Returns as soon as encoding
    completes (~5 ms); the serial write runs in the background.
    """
    t0 = time.perf_counter()
    try:
        await pool.print_receipt_json(data)
        dur = time.perf_counter() - t0
        print_duration_seconds.labels(action="print_receipt_json").observe(dur)
        print_jobs_total.labels(action="print_receipt_json", result="success").inc()
        return JSONResponse({"success": True})
    except Exception as e:
        print_jobs_total.labels(action="print_receipt_json", result="error").inc()
        logger.error("[print_receipt_json] %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
