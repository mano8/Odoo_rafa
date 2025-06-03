# Run scripts from fastapi

To run bash_scripts from Fastapi end points we need add permissions to sudoers.
Here user who run `hw_proxy` service is `hw_user`.

## Add `hw_user` to sudoers

> **Warning**
> Do not add this user to group sudo.
Add Permission to run bash scripts as `root` without password

```bash
sudo visudo /etc/sudoers.d/zepos
```

```
# Allow "hw_user" user to run only these scripts as root, without password
Defaults:hw_user !requiretty

hw_user ALL=(root) NOPASSWD: \
    /opt/hw_proxy/hw_proxy/scripts/reboot.sh, \
    /opt/hw_proxy/hw_proxy/scripts/shutdown.sh, \
    /opt/hw_proxy/hw_proxy/scripts/docker_restart_container.sh, \
    /opt/hw_proxy/hw_proxy/scripts/update_hw_proxy.sh
```

Verrify

```bash
# Optional ensure file owner and permission
sudo chown root:root /etc/sudoers.d/hw_user
sudo chmod 440 /etc/sudoers.d/hw_user
# optional if modified
sudo visudo -c -f /etc/sudoers
# Control syntax
sudo visudo -c -f /etc/sudoers.d/hw_user
```

## Add extra user to ensure never break down sudoers

### Create user 

```bash
sudo adduser <user_name>
```

### Add user to group `sudo`

```bash
sudo usermod -aG sudo <user_name>
```

### Verrify

```bash
getent group sudo
```
