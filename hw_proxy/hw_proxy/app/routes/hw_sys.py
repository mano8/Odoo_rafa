"""
Api routes for hw_sys module
"""
import logging
import asyncio
import psutil
import subprocess
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from hw_proxy.schemas.hw_sys import JournalQuery
from hw_proxy.tools.utils import HwUtils
from hw_proxy.core.config import settings


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
async def get_printer_status():
    try:
        result = HwUtils.get_printer_global_status()
        return JSONResponse(result)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/print_ticket")
async def print_ticket():
    try:
        result = HwUtils.print_dummy_ticket()
        return JSONResponse(result)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/open_cashdrawer")
async def open_cashdrawer():
    try:
        result = HwUtils.open_cash_drawer()
        return JSONResponse(result)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
