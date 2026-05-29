"""
Api routes for hw_sys module
"""
import asyncio
import logging
import os
import subprocess
import psutil
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from hw_proxy.core.deps import get_printer_pool
from hw_proxy.core.printer_pool import PrinterPool
from hw_proxy.schemas.hw_sys import JournalQuery
from hw_proxy.tools.utils import HwUtils


logger = logging.getLogger("hw_proxy")

router = APIRouter(prefix="/system", tags=["system"])

_SYSTEMD_SERVICES = ["hw_proxy", "odoo-pos", "monitoring", "serial-config"]
_DOCKER_CONTAINERS = ["traefik", "fiesta_db", "hw_status_service", "fiesta_odoo"]

# journald priority ceiling per log level (includes all levels at or above)
_JOURNAL_PRIORITY = {"error": "err", "warning": "warning", "info": "info"}

# keywords that mark important lines in docker container stdout/stderr
_DOCKER_IMPORTANT = ("error", "warn", "critical", "fatal", "exception", "traceback")


_SYS_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def _run_cmd(cmd: list[str], timeout: int = 10) -> tuple[str, str]:
    """Run a subprocess and return (stdout, stderr). Never raises."""
    env = os.environ.copy()
    env["PATH"] = _SYS_PATH
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "", "Command timed out"
    except FileNotFoundError:
        return "", f"Command not found: {cmd[0]}"
    except Exception as exc:
        return "", str(exc)


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
        await pool.cut()
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


@router.get("/logs", response_class=PlainTextResponse)
async def get_service_logs(
    service: str = Query(..., description="Service name (systemd or docker container)"),
    lines: int = Query(100, ge=1, le=500, description="Max lines to return"),
    level: str = Query("warning", description="Log level: error, warning, info, all"),
) -> str:
    """Return recent logs for a service, filtered to the given level."""
    if service in _SYSTEMD_SERVICES:
        svc_unit = service if service.endswith(".service") else f"{service}.service"
        cmd = [
            "journalctl", "-u", svc_unit,
            "-n", str(lines),
            "--no-pager",
            "--output=short-iso",
        ]
        if level != "all":
            cmd.append(f"-p{_JOURNAL_PRIORITY.get(level, 'warning')}")
        stdout, stderr = await asyncio.to_thread(_run_cmd, cmd)
        if not stdout and stderr:
            return f"[Error fetching logs for {service}]\n{stderr}"
        return stdout or f"[No logs found for {service} at level={level}]"

    if service in _DOCKER_CONTAINERS:
        cmd = ["docker", "logs", "--tail", str(lines), service]
        stdout, stderr = await asyncio.to_thread(_run_cmd, cmd)
        # docker writes app logs to stderr by convention; merge both streams
        combined = "\n".join(filter(None, [stderr, stdout])).strip()
        if not combined:
            return f"[No logs found for container {service}]"
        if level != "all":
            filtered = [
                ln for ln in combined.splitlines()
                if any(p in ln.lower() for p in _DOCKER_IMPORTANT)
            ]
            return "\n".join(filtered) or f"[No {level}+ logs found for {service}]"
        return combined

    return f"[Unknown service: {service}]"


@router.get("/services/status")
async def get_services_status() -> dict:
    """Return running status for all managed systemd and docker services."""
    services = []

    for svc in _SYSTEMD_SERVICES:
        svc_unit = svc if svc.endswith(".service") else f"{svc}.service"
        stdout, err = await asyncio.to_thread(_run_cmd, ["systemctl", "is-active", svc_unit])
        state = stdout.strip() if stdout.strip() else (err.strip() or "unknown")
        services.append({
            "name": svc,
            "type": "systemd",
            "status": state,
            "active": state == "active",
        })

    for container in _DOCKER_CONTAINERS:
        stdout, err = await asyncio.to_thread(
            _run_cmd, ["docker", "inspect", "--format", "{{.State.Status}}", container]
        )
        state = stdout.strip() if stdout.strip() else "not found"
        services.append({
            "name": container,
            "type": "docker",
            "status": state,
            "active": state == "running",
        })

    return {"services": services}
