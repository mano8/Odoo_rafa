# Post-Deploy Security Hardening

Complete these steps **before** exposing the stack on your LAN.
Each section describes what to do and why it matters.

---

## 1. Dedicated `hw_user` — Groups and Permissions

The `hw_proxy` service must run as a non-root user with the minimum group memberships needed for hardware access.

### Create the user (if not already done)

```bash
sudo adduser --disabled-password --gecos "" hw_user
```

### Add to device groups

```bash
sudo usermod -aG dialout,lp hw_user
```

| Group     | Grants access to                              |
| --------- | --------------------------------------------- |
| `dialout` | `/dev/ttyACM*` and `/dev/ttyUSB*` (serial)   |
| `lp`      | USB printer devices on some distributions    |

> **Never** add `hw_user` to the `sudo` group.
> The only elevated actions it needs (`reboot`, `shutdown`) are granted via a narrow `sudoers` entry — see `hw_proxy/hw_proxy/scripts/README.md`.

### Verify

```bash
id hw_user
# uid=...(hw_user) gid=...(hw_user) groups=...,dialout,lp
```

---

## 2. Firewall — `hw_proxy` Port (9002)

`hw_proxy` binds exclusively to `10.254.254.1:9002` (the `docker0-mgmt` management dummy
interface). It is structurally unreachable from the LAN or any external network — no
firewall rule is needed to protect it.

Traefik (running in Docker) reaches it via the same management interface. POS clients
never connect to port 9002 directly; they go through Traefik on port 9001 (HTTPS).

Restrict the Traefik public ports to LAN with `ufw`:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 9000 comment 'Odoo LAN'
sudo ufw allow from 192.168.1.0/24 to any port 9001 comment 'hw_status/hw_proxy LAN'
# Allow Docker bridge networks to reach hw_proxy on the management interface
sudo ufw allow from 172.16.0.0/12 to 10.254.254.1 port 9002 comment 'hw_proxy Docker mgmt only'
sudo ufw enable
sudo ufw status verbose
```

> Port 8080 (Traefik dashboard) should be accessible only from `127.0.0.1` or a trusted admin host.

---

## 3. Change All Default Passwords

### PostgreSQL

In `.env` (and `odoo/config/odoo.conf`), replace every occurrence of `changethis`:

```bash
nano docker-compose/odoo_prod/.env
# DB_PASSWORD=<strong-random-password>

nano docker-compose/odoo_prod/odoo/config/odoo.conf
# db_password = <same-strong-random-password>
```

### Odoo admin master password

Set a strong master password in `odoo.conf`:

```ini
[options]
admin_passwd = <strong-random-password>
```

### `hw_proxy` SECRET_KEY

In `hw_proxy/hw_proxy/.env`:

```bash
SECRET_KEY="<random-64-char-string>"
```

Generate one:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 4. Production Environment Flags

Ensure `hw_status_service` in `docker-compose.yml` uses production settings (already corrected in this repo):

```yaml
environment:
  ENVIRONMENT: production
  SET_OPEN_API: false
  SET_DOCS: false
  SET_REDOC: false
```

Exposing `/docs`, `/redoc`, or `/openapi.json` in production leaks your API surface area.

---

## 5. Traefik Dashboard

The Traefik dashboard (port 8080) is useful during setup but should not be left open.

### Option A — Bind only to localhost (recommended for single-machine setups)

Edit `docker-compose.yml` and change the port mapping:

```yaml
ports:
  - "127.0.0.1:8080:8080"   # was: "8080:8080"
```

### Option B — Add basic-auth middleware

In `traefik/dynamic_conf.yml`:

```yaml
http:
  middlewares:
    dashboard-auth:
      basicAuth:
        users:
          - "admin:$apr1$..."   # generate with: htpasswd -nb admin <password>
```

Then attach the middleware to the dashboard router in `traefik.yml`.

---

## 6. TLS Certificate Renewal

Local certificates are generated with a validity of **825 days** (~2.25 years).
Mark a calendar reminder to regenerate them before expiry:

```bash
# Check expiry date of your current cert
openssl x509 -noout -enddate \
  -in docker-compose/odoo_prod/traefik/certs/local-cert.crt
```

To regenerate:

```bash
cd docker-compose
bash scripts/generate_traefick_certs.sh traefik-client.local 192.168.1.146 local-cert
```

Then re-import `traefik/certs/ca.pem` into your browser/OS trust store.

> If you distributed the `.pfx` file, note it was exported without a password.
> Store it in a location only trusted admins can read, or regenerate it with a passphrase.

---

## 7. Docker mTLS Certificates

The Docker daemon is secured with mutual TLS certificates (see `docker/README.md`).
These are also generated with an 825-day validity. Treat them the same as the Traefik certs.

```bash
# Check Docker daemon cert expiry
openssl x509 -noout -enddate -in docker/certs/server-cert.pem
```

---

## 8. Review `sudoers` Entry

The `hw_user` sudoers file must allow **only** the two reboot/shutdown scripts:

```
hw_user ALL=(root) NOPASSWD: \
    /opt/hw_proxy/hw_proxy/scripts/reboot.sh, \
    /opt/hw_proxy/hw_proxy/scripts/shutdown.sh
```

After editing, validate syntax:

```bash
sudo visudo -c -f /etc/sudoers.d/hw_user
```

Ensure the file permissions are correct:

```bash
sudo chown root:root /etc/sudoers.d/hw_user
sudo chmod 440 /etc/sudoers.d/hw_user
```

---

## 9. Periodic Log Audit

Review these regularly for unexpected activity:

```bash
# hw_proxy service logs
sudo journalctl -xeu hw_proxy.service --since "7 days ago"

# Traefik container logs
sudo journalctl -f CONTAINER_NAME=<traefik-container-name>

# List stored database backups
ls -lh /opt/hw_proxy/backups/
```

Remove old backups that are no longer needed:

```bash
find /opt/hw_proxy/backups/ -name "*.zip" -mtime +30 -delete
```

---

## 10. Keep Dependencies Updated

```bash
# Update Python dependencies inside hw_proxy virtualenv
pip install --upgrade -r /opt/hw_proxy/hw_proxy/requirements.txt

# Pull latest Odoo and PostgreSQL images
sudo docker pull odoo:18.0
sudo docker pull postgres:13.21-alpine3.20
sudo docker compose up -d
```

---

## Summary Checklist

- [ ] `hw_user` added to `dialout` and `lp` groups
- [ ] `ufw` rules restricting port 9002 to LAN subnet
- [ ] All `changethis` passwords replaced (DB, Odoo admin, SECRET_KEY)
- [ ] `hw_status_service` running with `ENVIRONMENT: production`, all `SET_*` flags false
- [ ] Traefik dashboard restricted to localhost or protected with basic auth
- [ ] TLS certificate expiry date noted in calendar (825 days from generation)
- [ ] Docker mTLS certificate expiry date noted in calendar
- [ ] `sudoers` entry validated with `visudo -c`
- [ ] No `.pfx` or `.key` files readable by non-admin users
