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

