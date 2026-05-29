# Set up Odoo Server

Here Server run on Linux mint XFCE 22.1, you must adapt commands for other system.

## Install, Secure and Configure Docker

> [See this document](https://github.com/mano8/Odoo_rafa/blob/1c8800351c1dac261c852ef76b5954c7dfa22c82/docker/README.md)

## Boot to Console Only (Disable Automatic X)

On Mint XFCE 22.1 the graphical session is usually started by a display manager (LightDM). To boot to a text console instead:

- 1. Set the default systemd target to multi-user (no GUI):

```bash
sudo systemctl set-default multi-user.target
```

  > This makes the system boot to the multi-user (non-graphical) runlevel.

- 2. Disable the display manager (LightDM) so it won’t auto-start:

```bash
sudo systemctl disable lightdm.service
sudo systemctl mask   lightdm.service
```

  > `mask` makes it impossible to start (unless you `unmask` it).

- 3. Reboot to verify you land at a text login prompt.

```bash
sudo reboot now
```

### Starting XFCE Manually with `startx`

- 1. Install `xinit` if it’s not already present:

```bash
sudo apt update && sudo apt install xinit
```

- 2. Create or update your `~/.xinitrc` to launch XFCE:

```bash
echo "exec startxfce4" > ~/.xinitrc
chmod +x ~/.xinitrc
```

- 3. Run

```bash
startx
```
  > This will read `~/.xinitrc` and start XFCE in the current session.
  > When you exit XFCE, you’ll return to the console login.

### Restore Graphical Boot

If in the future you want to restore the GUI at startup:

```bash
sudo systemctl unmask   lightdm.service
sudo systemctl enable   lightdm.service
sudo systemctl set-default graphical.target
```

Then on reboot you’ll return to the XFCE login screen.

---

## hw_proxy Deployment

### Standard deploy (code changes only)

```bash
cd /opt/Odoo_rafa && sudo git pull origin Secure
sudo /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/update_hw_proxy.sh
sudo systemctl restart hw_proxy
```

`update_hw_proxy.sh` automatically:

- Syncs Python code to `/opt/hw_proxy/hw_proxy/`
- Installs/upgrades pip requirements
- Sets `hw_user:hw_user` ownership and `750` on all `.sh` scripts in the deployed copy

> **Note:** Python reads bash scripts from the **repo path** (`/opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/`), not the deployed copy.
> Scripts committed with `100755` in git will be executable after `git pull`.

---

### Adding a new bash script

When a new `.sh` script is added to `hw_proxy/hw_proxy/scripts/` and needs `sudo` access, follow these steps **once** on the server after deploying:

#### 1. Verify the script is executable after pull

```bash
ls -la /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/
```

Scripts must show `-rwxr-x---` (mode 750). If not:

```bash
sudo chmod 750 /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/<script_name>.sh
sudo chown hw_user:hw_user /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/<script_name>.sh
```

#### 2. Add the script to sudoers

```bash
sudo visudo /etc/sudoers.d/hw_user
```

The file must look like this (add each new script with a comma + backslash on the previous line):

```sudoers
# Allow "hw_user" user to run only these scripts as root, without password
Defaults:hw_user !requiretty
Defaults:hw_user !logfile, !syslog, !pam_session

hw_user ALL=(ALL) NOPASSWD: \
    /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/reboot.sh, \
    /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/shutdown.sh, \
    /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/get_logs.sh, \
    /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/get_services_status.sh
```

#### 3. Validate sudoers syntax (never skip this)

```bash
sudo visudo -c -f /etc/sudoers.d/hw_user
```

Expected output: `/etc/sudoers.d/hw_user: parsed OK`

#### 4. Fix sudoers file permissions

```bash
sudo chown root:root /etc/sudoers.d/hw_user
sudo chmod 440 /etc/sudoers.d/hw_user
```

#### 5. Smoke-test the script as hw_user

```bash
sudo -u hw_user sudo /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/get_services_status.sh
sudo -u hw_user sudo /opt/Odoo_rafa/hw_proxy/hw_proxy/scripts/get_logs.sh hw_proxy 20 warning
```

Both should return output without a password prompt.
