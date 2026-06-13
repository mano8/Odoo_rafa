# Controllable ESC/POS printer emulator (TCP transport).
#
# socat + pyserial are installed so the serial/PTY path also works *inside* the
# container (the Windows dev host has no socat); the default CMD serves TCP,
# which is the clean cross-container transport for the compose stack.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/emulated_printer

RUN apt-get update && apt-get install -y --no-install-recommends \
      socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/emulated_printer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x run_local.sh

EXPOSE 9100

CMD ["python", "server.py", "--config", "config/pp6800.yml", \
     "--transport", "tcp", "--host", "0.0.0.0", "--port", "9100"]
