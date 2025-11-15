# 🔐 Generate mTLS Certificates for Docker Daemon Socket

This guide describes how to **manually create and configure mTLS certificates** for securing the **Docker API socket** (`tcp://10.254.254.1:2376`).

It is designed for setups where you want **full control** over the certificate generation process, without using the automated `manage_docker_certs.sh` script.

---

## 🧭 Overview

The mTLS setup ensures:

* Only trusted clients (with valid certificates) can connect to the Docker daemon.
* Communication between Docker clients and the daemon is **encrypted and authenticated**.
* The certificates are signed by a local **Certificate Authority (CA)** that you control.

---

## 📁 1. Create Docker Certificates Directory

Create and secure the folder for server-side certificates:

```bash
sudo mkdir -p /etc/docker/certs
sudo chmod 700 /etc/docker/certs
sudo chown root:root /etc/docker/certs
cd /etc/docker/certs
```

---

## 🔑 2. Generate CA (Certificate Authority)

The CA is used to sign both server and client certificates.

```bash
sudo openssl genrsa -out ca-key.pem 4096

sudo openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 \
  -out ca.pem -subj "/C=ES/ST=Andalusia/L=Almería/O=Docker_Certs/CN=ca.local"
```

> 🔒 The CA key (`ca-key.pem`) must remain private and **never** be shared.

---

## 🖥️ 3. Generate Server Certificates

The Docker daemon uses these certificates to authenticate itself to clients.

### Generate key and signing request

```bash
sudo openssl genrsa -out server-key.pem 2048
sudo openssl req -new -key server-key.pem -out server.csr -config openssl.conf
```

> Ensure you have an `openssl.conf` file with a `[ req_ext ]` section defining SANs (Subject Alternative Names) for:
>
> ```bash
> IP.1 = 10.254.254.1
> IP.2 = 127.0.0.1
> DNS.1 = localhost
> DNS.2 = docker.local
> ```

### Sign the server certificate

```bash
sudo openssl x509 -req -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial \
  -out server-cert.pem -days 3650 -extensions req_ext -extfile openssl.conf
```

---

## 👤 4. Generate Client Certificates

Client certificates authenticate Docker clients (e.g. Traefik or management scripts).

```bash
cd /opt/Odoo_rafa/docker/certs

openssl genrsa -out client-key.pem 2048

openssl req -new -key client-key.pem -out client.csr \
  -subj "/C=ES/ST=Andalusia/L=Almería/O=Traefik/CN=traefik-client"

sudo openssl x509 -req -in client.csr \
  -CA /etc/docker/certs/ca.pem -CAkey /etc/docker/certs/ca-key.pem -CAcreateserial \
  -out client-cert.pem -days 3650
```

> 🧩 Each client (e.g., Traefik, local admin tools) should have its **own certificate pair**.

---

## 🔒 5. Secure Certificate Permissions

### Server certificates

```bash
sudo chmod -R 600 /etc/docker/certs
sudo chown -R root:docker /etc/docker/certs
```

### Client certificates

```bash
# Retrieve dockremap UID 
cat /etc/subuid
# Example output:
# myUser:100000:65536
# dockremap:231072:65536

# Copy CA for client verification
sudo cp /etc/docker/certs/ca.pem /opt/Odoo_rafa/docker/certs/ca.pem
sudo chmod -R 755 /opt/Odoo_rafa/docker/certs
sudo chown -R 231072:231072 /opt/Odoo_rafa/docker/certs
```

> The `231072` UID corresponds to the remapped user inside Docker (`dockremap`).
> Update this according to your `/etc/subuid` output.

---

## 🔍 6. Verify Files

### Server side

```bash
sudo ls -l /etc/docker/certs/
```

Expected:

```bash
-rw------- 1 root docker ca.pem
-rw------- 1 root docker server-cert.pem
-rw------- 1 root docker server-key.pem
```

### Client side

```bash
ls -l /opt/Odoo_rafa/docker/certs/
```

Expected:

```bash
-rw-r--r-- 1 dockremap dockremap ca.pem
-rw-r--r-- 1 dockremap dockremap client-cert.pem
-rw-r--r-- 1 dockremap dockremap client-key.pem
```

---

## 🧩 7. Test mTLS Connectivity

Once Docker is configured to listen on the mTLS socket (`tcp://10.254.254.1:2376`):

```bash
cd /opt/Odoo_rafa/docker/certs

sudo docker --tlsverify \
  --tlscacert=ca.pem \
  --tlscert=client-cert.pem \
  --tlskey=client-key.pem \
  -H tcp://10.254.254.1:2376 version
```

A successful connection returns version details from the Docker daemon.

---

## ⚠️ Notes & Best Practices

| Topic                   | Recommendation                                               |
| ----------------------- | ------------------------------------------------------------ |
| **CA Lifetime**         | Use `-days 3650` for 10-year CA validity (adjust as needed). |
| **Server Cert Renewal** | Renew every 1–2 years to prevent expiry downtime.            |
| **File Permissions**    | `600` for server certs; `755` for client certs.              |
| **SAN Configuration**   | Always include all IPs/DNS names used for Docker API access. |
| **Separation of Keys**  | Never share private keys between server and clients.         |

---

## 🧠 Related Files

| File                                          | Purpose                                |
| --------------------------------------------- | -------------------------------------- |
| `/etc/docker/certs/ca.pem`                    | Root CA certificate                    |
| `/etc/docker/certs/server-cert.pem`           | Docker daemon certificate              |
| `/etc/docker/certs/server-key.pem`            | Docker daemon private key              |
| `/opt/Odoo_rafa/docker/certs/client-cert.pem` | Client authentication certificate      |
| `/opt/Odoo_rafa/docker/certs/client-key.pem`  | Client private key                     |
| `/opt/Odoo_rafa/docker/certs/ca.pem`          | Client-side CA for verification        |
| `/etc/docker/certs/openssl.conf`              | OpenSSL configuration with SAN entries |

---

## ✅ Summary

After following this guide:

* The Docker daemon will authenticate clients using mTLS.
* Only trusted clients with valid certificates can manage Docker.
* Communications are encrypted and verified end-to-end.
