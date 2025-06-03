# Generate mTls Certificates for docker demon sock

- Move to docker certs folder

```bash
sudo mkdir -p /etc/docker/certs
sudo chmod 700 /etc/docker/certs
sudo chown root:root /etc/docker/certs
cd /etc/docker/certs
```

- Generate CA private key

```bash
sudo openssl genrsa -out ca-key.pem 4096

sudo openssl req -x509 -new -nodes -key ca-key.pem -sha256 -days 3650 -out ca.pem -subj "/C=ES/ST=Andalusia/L=Almería/O=Docker_Certs/CN=ca.local"
```

- Generate server certificates

```bash
sudo openssl genrsa -out server-key.pem 2048

sudo openssl req -new -key server-key.pem -out server.csr -config openssl.conf

sudo openssl x509 -req -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 3650 -extensions req_ext -extfile openssl.conf
```

- Generate client certificates

```bash
cd /opt/Odoo_rafa/docker/certs

openssl genrsa -out client-key.pem 2048

openssl req -new -key client-key.pem -out client.csr -subj "/C=ES/ST=Andalusia/L=Almería/O=Traefik/CN=traefik-client"

sudo openssl x509 -req -in client.csr -CA /etc/docker/certs/ca.pem -CAkey /etc/docker/certs/ca-key.pem -CAcreateserial -out client-cert.pem -days 3650
```

- Config Docker server certificates permisions

```bash
sudo chmod -R 600 /etc/docker/certs
sudo chown -R root:docker /etc/docker/certs
```

- Config Docker client certificates permisions

```bash
# Retrieve dockremap UID 
cat /etc/subuid
# Example: myUser:100000:65536
# Example: dockremap:231072:65536
# Copy ca.pem
sudo cp /etc/docker/certs/ca.pem /opt/Odoo_rafa/docker/certs/ca.pem
sudo chmod -R 755 /opt/Odoo_rafa/docker/certs
sudo chown -R 231072:231072 /opt/Odoo_rafa/docker/certs
```