# Fix Server IP to `192.168.1.146`

To Work Correctly this server need static IP `192.168.1.146`.
Docker compose containers and FastApi service are configured with this static IP.

## Configure NetworkManager

> **Warning**
> The above script need `ipcalc` deb package to work properly.
> To ensure is already intalled run `ipcalc -v`
> If not installed run `sudo apt install ipcalc`

```bash
sudo nano /etc/NetworkManager/dispatcher.d/99-static-ip-or-dhcp.sh
```

and copy content of `99-static-ip-or-dhcp.sh` in current path.


### Apply changes

```bash
sudo chmod +x /etc/NetworkManager/dispatcher.d/99-static-ip-or-dhcp.sh
sudo systemctl restart NetworkManager
```

### Test:

```bash
ip a | grep 192.168.1.146
# Example : inet 192.168.1.146/24 brd 192.168.1.255 scope global noprefixroute enp5s0

journalctl -t static-ip -n 20

# Must have line like: Detected subnet 192.168.1.0/24. Setting static IP 192.168.1.146/24 on enp5s0
```

