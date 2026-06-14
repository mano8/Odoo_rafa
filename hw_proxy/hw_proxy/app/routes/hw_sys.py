"""
Api routes for hw_sys module
"""
import asyncio
import logging
import subprocess
import psutil
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from hw_proxy.core.deps import get_printer_pool
from hw_proxy.core.printer_pool import PrinterPool
from hw_proxy.schemas.hw_sys import JournalQuery
from hw_proxy.schemas.printer import PrintSettings
from hw_proxy.schemas.receipt import PrintReceiptJsonRequest, ReceiptLine
from hw_proxy.tools.utils import HwUtils

_KNOWN_SERVICES = {
    "hw_proxy", "odoo-pos", "monitoring",
    "traefik", "fiesta_db", "hw_status_service", "fiesta_odoo",
    "grafana", "prometheus",
}

logger = logging.getLogger("hw_proxy")

router = APIRouter(prefix="/system", tags=["system"])


@router.post("/shutdown")
async def system_shutdown():
    try:
        HwUtils.run_bash_script(
            script="shutdown.sh"
        )
        return JSONResponse({
            "success": True,
            "message": "System shutting down"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reboot")
async def system_reboot():
    try:
        HwUtils.run_bash_script(
            script="reboot.sh"
        )
        return JSONResponse({"success": True, "message": "System rebooting"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart-container/{container_name}")
async def restart_container(
    container_name: str
):
    try:
        result = HwUtils.run_bash_script(
            script="docker_restart_container.sh",
            args=[container_name]
        )
        return JSONResponse({"success": True, "message": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/docker_journal")
async def docker_journal(query: JournalQuery):
    try:
        cmd = ["journalctl", "-u", query.unit, "-o", "short-iso"]
        if query.since:
            # parse since time or relative time like '5min'
            since_time = HwUtils.parse_relative_time(query.since)
            if since_time:
                cmd += ["--since", since_time.isoformat()]
        if query.until:
            until_time = HwUtils.parse_relative_time(query.until)
            if until_time:
                cmd += ["--until", until_time.isoformat()]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip())
        return {"success": True, "unit": query.unit, "logs": proc.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connected_devices")
async def connected_devices():
    devices = []
    try:
        for device in psutil.disk_partitions(all=True):
            devices.append({
                "device": device.device,
                "mountpoint": device.mountpoint,
                "fstype": device.fstype,
                "opts": device.opts,
            })
        # Add more info if needed
        return JSONResponse({"success": True, "devices": devices})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/serial_config")
async def serial_config(device: str = "/dev/ttyACM0"):
    try:
        # use stty to get config
        result = HwUtils.get_serial_config(
            devfile=device
        )
        return {"success": True, "device": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/printer_status")
async def get_printer_status(pool: PrinterPool = Depends(get_printer_pool)):
    try:
        esc_status = await pool.get_full_status()
        devfile = pool.devfile
        conection = HwUtils.get_printer_conection_status(devfile)
        try:
            serial_config = HwUtils.get_serial_config(devfile)
        except Exception:
            serial_config = None

        result = {"devicePortType": "SERIAL"}
        result.update({
            "printerOnline": esc_status.get("is_online"),
            "paperOk": esc_status.get("paper_status") == "ok",
            "paperLow": esc_status.get("paper_status") == "near_end",
        })
        if isinstance(conection, dict):
            result["connected"] = conection.get("status") == "connected"
        if isinstance(serial_config, dict):
            serial_config.update({"readStatus": True, "writeStatus": True})
            result["serialInfo"] = serial_config
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/print_ticket")
async def print_ticket(pool: PrinterPool = Depends(get_printer_pool)):
    try:
        req = PrintReceiptJsonRequest(
            lines=[
                ReceiptLine(t="text", v="*** TEST PRINT ***", c="center", b=True),
                ReceiptLine(t="div"),
                ReceiptLine(t="row", l="hw_proxy", r="OK"),
                ReceiptLine(t="row", l="Printer", r="OK"),
                ReceiptLine(t="div"),
                ReceiptLine(t="text", v="Test OK", c="center"),
            ],
            char_size=1,
            cut=True,
            open_cashdrawer=False,
        )
        await pool.print_receipt_json(req)
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/open_cashdrawer")
async def open_cashdrawer(pool: PrinterPool = Depends(get_printer_pool)):
    try:
        await pool.open_cashdrawer()
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ---------------------------------------------------------------------------
# Printer pipeline tuning & recovery (driven by the hw_status UI)
# ---------------------------------------------------------------------------


@router.get("/print_settings")
async def get_print_settings(
    pool: PrinterPool = Depends(get_printer_pool),
) -> PrintSettings:
    """Return the live print-pipeline settings."""
    return pool.get_settings()


@router.post("/print_settings")
async def set_print_settings(
    settings: PrintSettings,
    pool: PrinterPool = Depends(get_printer_pool),
) -> PrintSettings:
    """Apply new print-pipeline settings and return the live values."""
    try:
        return pool.update_settings(**settings.model_dump())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/clear_print_queue")
async def clear_print_queue(pool: PrinterPool = Depends(get_printer_pool)):
    """Discard all pending print jobs without printing them."""
    try:
        return JSONResponse({"cleared": pool.clear_queue()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/reset_printer")
async def reset_printer(pool: PrinterPool = Depends(get_printer_pool)):
    """Recover an overflowed printer: flush the queue and clear its buffers."""
    try:
        cleared = await pool.reset_printer()
        return JSONResponse({"success": True, "cleared": cleared})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/print_test_batch")
async def print_test_batch(
    count: int = Query(5, ge=1, le=100, description="Number of receipts to enqueue"),
    lines: int = Query(6, ge=1, le=50, description="Body lines per receipt"),
    pool: PrinterPool = Depends(get_printer_pool),
):
    """Enqueue ``count`` numbered synthetic receipts to exercise the pipeline.

    Lets the whole queue/strategy/recovery path be driven from the UI or
    Swagger with no Odoo in the loop.
    """
    try:
        for i in range(1, count + 1):
            receipt_lines = [
                ReceiptLine(
                    t="text", v=f"*** TEST {i}/{count} ***", c="center", b=True
                ),
                ReceiptLine(t="div"),
            ]
            for j in range(1, lines + 1):
                receipt_lines.append(
                    ReceiptLine(t="row", l=f"line {j}", r=f"{i}.{j}")
                )
            receipt_lines.append(ReceiptLine(t="div"))
            req = PrintReceiptJsonRequest(
                lines=receipt_lines,
                char_size=1,
                cut=True,
                open_cashdrawer=False,
            )
            await pool.print_receipt_json(req)
        return JSONResponse({"queued": count})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/logs", response_class=PlainTextResponse)
async def get_service_logs(
    service: str = Query(..., description="Service name"),
    lines: int = Query(100, ge=1, le=500, description="Max lines to return"),
    level: str = Query("warning", description="Log level: error, warning, info, all"),
) -> str:
    """Return recent logs for a service via get_logs.sh (journald)."""
    if service not in _KNOWN_SERVICES:
        return f"[Unknown service: {service}]"
    try:
        result = await asyncio.to_thread(
            HwUtils.run_bash_script, "get_logs.sh", [service, str(lines), level]
        )
        return result or f"[No logs found for {service} at level={level}]"
    except RuntimeError as e:
        return f"[Error fetching logs for {service}]: {e}"


@router.get("/services/status")
async def get_services_status() -> dict:
    """Return running status for all managed services via get_services_status.sh."""
    try:
        output = await asyncio.to_thread(HwUtils.run_bash_script, "get_services_status.sh")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    services = []
    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) == 3:
            name, svc_type, status = parts
            services.append({
                "name": name,
                "type": svc_type,
                "status": status,
                "active": status in ("active", "running"),
            })
    return {"services": services}
