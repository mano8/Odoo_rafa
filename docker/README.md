# 🐳 Install, Secure, and Configure Docker (with mTLS and `userns-remap`)

This guide explains how to install Docker securely on **Ubuntu**, enable **user namespace remapping** (`userns-remap`) for host isolation, configure **mutual TLS (mTLS)** for authenticated access to the Docker API, and tune **journald** logging to control disk usage.

---

## 🔹 1. Uninstall Conflicting Packages

Remove any existing or conflicting Docker-related packages before installing the official version:

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg
done
```

---

## 🔹 2. Install Docker Engine

### Add Docker’s Official Repository

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Add the repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
```

### Install Engine, CLI, and Compose

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Verify Installation

```bash
sudo docker run hello-world
```

---

## 🔹 3. Enable `userns-remap` for Host Isolation

Docker’s **user namespace remapping** ensures containers run as unprivileged remapped UIDs/GIDs on the host, improving isolation.

### Check UID/GID mappings

```bash
grep -E '^(root|dockremap)' /etc/subuid /etc/subgid || true
```

Example output:

```bash
root:100000:65536
dockremap:165536:65536
```

### Configure Docker Daemon

```bash
sudo nano /etc/docker/daemon.json
```

Paste:

```json
{
  "userns-remap": "default",
  "experimental": false,
  "storage-driver": "overlay2",
  "log-driver": "journald"
}
```

> 💡 The `"default"` value automatically creates a `dockremap` user for UID/GID remapping.

Restart Docker:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Validate:

```bash
getent passwd dockremap
id dockremap
```

Example output:

```bash
dockremap:x:997:985::/home/dockremap:/bin/sh
uid=997(dockremap) gid=985(dockremap) groups=985(dockremap)
```

---

## 🔹 4. Configure Secure Docker API with mTLS

Docker’s REST API should **never** be exposed over TCP without TLS and authentication.
You’ll use **mutual TLS (mTLS)**, meaning both client and server authenticate with certificates.

### Define the Management IP

```bash
export DOCKER_HOST_IP=10.254.254.1
```

### Generate Certificates

```bash
sudo DOCKER_HOST_IP="$DOCKER_HOST_IP" /opt/Odoo_rafa/docker/scripts/manage_docker_certs.sh generate
```

> To remove certificates later:

```bash
sudo /opt/Odoo_rafa/docker/scripts/manage_docker_certs.sh remove
```

Certificates are stored under:

```bash
/etc/docker/certs/
├── ca.pem
├── server-cert.pem
├── server-key.pem
├── client-cert.pem
└── client-key.pem
```

> 💡 Alternatively, see [Manual Certificate Generation Guide](./certs/README.md)
> for full OpenSSL-based manual steps and permission handling.

---

## 🔹 5. Add a Dummy Management Interface

To bind the Docker API securely to an isolated address, create a **dummy interface**.

### Ensure NetworkManager Is Active

```bash
systemctl is-enabled NetworkManager
systemctl is-active NetworkManager
```

### Create Dummy Interface

```bash
sudo nmcli connection add type dummy ifname docker0-mgmt con-name docker0-mgmt ip4 "$DOCKER_HOST_IP"/32 autoconnect yes
sudo nmcli connection up docker0-mgmt
```

Verify:

```bash
ip addr show docker0-mgmt
nmcli device status | grep docker0-mgmt
```

You should see `docker0-mgmt` with IP `10.254.254.1`.

---

## 🔹 6. Enable mTLS in Docker Daemon

Edit `/etc/docker/daemon.json`:

```json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://10.254.254.1:2376"],
  "tls": true,
  "tlsverify": true,
  "tlscacert": "/etc/docker/certs/ca.pem",
  "tlscert": "/etc/docker/certs/server-cert.pem",
  "tlskey": "/etc/docker/certs/server-key.pem",
  "storage-driver": "overlay2",
  "userns-remap": "default",
  "experimental": false
}
```

### Override the Systemd Service

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo nano /etc/systemd/system/docker.service.d/override.conf
```

Paste:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --containerd=/run/containerd/containerd.sock
```

Reload and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Validate API Binding

```bash
sudo ss -tlnp | grep dockerd
```

Example output:

```bash
LISTEN 0 4096 10.254.254.1:2376 0.0.0.0:* users:(("dockerd",pid=16757,fd=4))
```

---

## 🔹 7. Test Remote TLS Access

```bash
cd /opt/Odoo_rafa/docker/certs

sudo docker --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=client-cert.pem \
  --tlskey=client-key.pem \
  -H tcp://10.254.254.1:2376 version
```

You should see version info from your Docker daemon — confirming secure mTLS communication.

---

## 🔹 8. Configure `journald` for Docker Logging

By default, Docker writes logs through **journald**, which can consume large amounts of disk space.
To control growth and enable automatic log rotation, configure journald limits.

### Create configuration file

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo nano /etc/systemd/journald.conf.d/00-docker.conf
```

### Add the following content

```ini
[Journal]
# Limit total disk space taken by all journal files
SystemMaxUse=1G
# Always leave at least this much free space on the filesystem
SystemKeepFree=100M

# Cap individual journal files to 100 MiB each
SystemMaxFileSize=100M
# Keep at most 10 archived journal files
SystemMaxFiles=10

# Runtime (volatile) journals in /run/log/journal
RuntimeMaxUse=200M
RuntimeKeepFree=50M
RuntimeMaxFileSize=50M
RuntimeMaxFiles=5

# Optionally expire entries older than 2 weeks
MaxRetentionSec=2week

# Compress archived journal files
Compress=yes
```

### Explanation

* `SystemMaxUse=` → Total space used by persistent logs (`/var/log/journal`)
* `SystemMaxFileSize=` → Size limit per file before rotation
* `SystemMaxFiles=` → Number of archived files retained
* `Runtime*` → Limits for temporary logs in `/run/log/journal`
* `MaxRetentionSec=` → Deletes entries older than the specified time
* `Compress=` → Compresses old logs automatically

### Apply and verify

```bash
sudo systemctl restart systemd-journald
sudo systemd-analyze cat-config systemd/journald.conf
```

---

## 🔹 9. Troubleshooting & Debugging

### Restart and View Logs

```bash
sudo systemctl restart docker
sudo journalctl -xeu docker.service
sudo journalctl -u docker.service --since "5 minutes ago"
```

### Run Daemon in Debug Mode

```bash
sudo dockerd --debug
```

---

## 🧠 Best Practices Summary

| Area                  | Recommendation                                           |
| --------------------- | -------------------------------------------------------- |
| **Access**            | Expose TCP socket **only** with mTLS                     |
| **User Mapping**      | Always enable `"userns-remap": "default"`                |
| **Logging**           | Use `journald` with size and retention caps              |
| **Network Isolation** | Bind API to dummy interface (no public exposure)         |
| **Certificates**      | Regenerate yearly; never reuse CA for unrelated services |
| **Permissions**       | Limit `/etc/docker/certs/` to `root:docker` (chmod 750)  |

---

✅ **You now have a hardened Docker setup**
with `userns-remap` for privilege isolation, **mutual TLS-secured API**, and **journald log control** — suitable for secure production or LAN-based automation.
