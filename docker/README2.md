Here is an improved version of your README with better structure, clarity, consistent formatting, and helpful comments. It keeps your technical content intact while enhancing readability and professionalism:

---

# Install, Secure, and Configure Docker (with mTLS and `userns-remap`)

This guide helps you install Docker securely on Ubuntu, enable `userns-remap` for user isolation, and set up **mutual TLS (mTLS)** for secure Docker API access.

---

## 1. Uninstall Conflicting Packages

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg"
done
```

---

## 2. Install Docker

### Add Docker's Official APT Repository

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update APT index
sudo apt-get update
```

### Install Docker Engine

```bash
sudo apt-get install -y \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

### Verify Docker Installation

```bash
sudo docker run hello-world
```

---

## 3. Enable `userns-remap` (Rootless Container Isolation)

### Check existing UID/GID mappings

```bash
grep -E '^(root|dockremap)' /etc/subuid /etc/subgid
cat /etc/subuid
# Example: myUser:100000:65536
```

### Configure `/etc/docker/daemon.json`

```bash
sudo nano /etc/docker/daemon.json
```

Paste:

```json
{
  "userns-remap": "default",
  "experimental": false,
  "storage-driver": "overlay2"
}
```

> 💡 Docker will auto-create the `dockremap` user and map UID/GID ranges.

### Restart Docker

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Validate

```bash
getent passwd dockremap
id dockremap
```

---

## 4. Set Up Secure Docker API with mTLS

### Define Host IP

```bash
export DOCKER_HOST_IP=10.254.254.1
```

### Generate Certificates

```bash
sudo DOCKER_HOST_IP="$DOCKER_HOST_IP" /opt/Odoo_rafa/docker/scripts/manage_docker_certs.sh generate
```

> 🔁 To remove certificates later:

```bash
sudo /opt/Odoo_rafa/docker/scripts/manage_docker_certs.sh remove
```

---

## 5. Configure Dummy Interface for API Binding

### Ensure NetworkManager Is Running

```bash
systemctl is-enabled NetworkManager
systemctl is-active NetworkManager
```

### Add Dummy Interface

```bash
sudo nmcli connection add type dummy ifname docker0-mgmt con-name docker0-mgmt ip4 "$DOCKER_HOST_IP"/32 autoconnect yes
sudo nmcli connection up docker0-mgmt
```

### Validate

```bash
ip addr show docker0-mgmt
nmcli device status | grep docker0-mgmt
```

---

## 6. Configure Docker Daemon for mTLS

Edit `/etc/docker/daemon.json`:

```json
{
  "hosts": [
    "unix:///var/run/docker.sock",
    "tcp://10.254.254.1:2376"
  ],
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

### Override Docker systemd Service

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

### Reload and Restart

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Check Docker Status

```bash
sudo docker info | grep -E 'Storage Driver|Userns|Experimental'
sudo systemctl status docker
```

---

## 7. Verify Remote TLS Connection

```bash
cd /opt/Odoo_rafa/docker/certs

sudo docker --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=client-cert.pem \
  --tlskey=client-key.pem \
  -H tcp://10.254.254.1:2376 version
```

---

## 8. Debugging

### Restart & Logs

```bash
sudo systemctl restart docker
sudo journalctl -xeu docker.service
sudo journalctl -u docker.service --since "5 minutes ago"
```

### Run Docker Daemon in Debug Mode

```bash
sudo dockerd --debug
```

---

Let me know if you want to:

* Add automatic setup scripts
* Support additional distros
* Include `iptables`/firewalld security rules

Would you like a diagram or a checklist version for this setup?
