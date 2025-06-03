# Odoo Docker compose

## Requirements

### Pos printer configuration for `hw_proxy_service`

By default Oddo need IotBox or compatible Epson printer to work.
Here FastApi `hw_proxy_service` App work as proxy service between Odoo and Pos Printer. This app needs access to serial port and correct serial configuration to work.

> See How to Setup `udev` rules
> See how to configure serial port

### Set up .env file

- Copy .env.example.txt to `.env`

```bash
cp ./env.example.txt ./.env
# Update env values
nano .env
```

- Copy hw_proxy.env.example.txt to `hw_proxy.env`

```bash
cp ./hw_proxy.env.example.txt ./hw_proxy.env
# Update hw_proxy env values
nano hw_proxy.env
```

### Set up Oddo config file

Add same data as `.env` file for db connection.

```bash
nano ./odoo/config/odoo.conf
```

### On Unix: Set Correct owners for docker volumes

> See [Understanding the Docker USER Instruction](https://www.docker.com/blog/understanding-the-docker-user-instruction/)

You must set volume files owner accordingelly with container user id.

- Get current user id in Odoo docker container

```bash
sudo docker run --rm odoo:18.0 id odoo
# Usually outputs:
> uid=100(odoo) gid=101(odoo) groups=101(odoo)
```

> See [Debian UID and GID classes](https://www.debian.org/doc/debian-policy/ch-opersys.html#uid-and-gid-classes)

- Control system host uid and gid

We need to ensure docker container UID and GID not colapse with system host UID and GID.

```bash
id -un -- 100
> dhcpcd
getent group 101
> messagebus:x:101:
```

In this system 

- Change volumes directory owners

```bash
sudo chown -R 100:101 ./odoo
```

## Build containers

First build containers from docker-compose

```bash
sudo docker compose up --build --remove-orphans
```

### Init data base in oddo container

Then run `fiesta_odoo` container with `bash` console.

```bash
sudo docker compose run fiesta_odoo bash
```

Then, in container console, run odoo CLI command to init data base.

```bash
odoo --init base --database DB_DATABASE --stop-after-init --db_host=fiesta_db --db_user DB_USER --db_password DB_PASSWORD  --without-demo=True

# On export end's up
exit
```

Now we can run containers, normally with Odoo db initialyzed.

```bash
sudo docker compose up --build --remove-orphans
```

## Systemd services

> See [Oddo Server Service]() to enable.

