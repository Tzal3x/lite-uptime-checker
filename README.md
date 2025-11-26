# lite-uptime-checker

A minimal uptime monitor that detects service downtime.

## TL;DR

The implementation is as simple as it gets:

1. A script (`checker.sh`) runs periodically to check the status of the service using `curl`.
2. The responses are saved in an SQLite3 database.
3. A web server (`uptime-webui-server.py`) provides a simple UI to view a plot and a table of the data.
4. Everything is registered as a systemd service.

## Installation

0. Make sure to install `sqlite3` and `python3` before proceeding.

```bash
sudo apt update 
sudo apt upgrade
sudo apt install sqlite3 python3
```

1. Create directories and user:
```bash
sudo mkdir -p /opt/uptime-checker /var/lib/uptime-checker
sudo useradd -r -s /bin/false uptime-checker || true
sudo chown uptime-checker:uptime-checker /var/lib/uptime-checker
```

2. Copy files:
```bash
sudo cp src/checker.sh /opt/uptime-checker/
sudo cp src/uptime-webui-server.py /opt/uptime-checker/
sudo cp src/index.html /opt/uptime-checker/
sudo chmod +x /opt/uptime-checker/*.sh
```

3. Install systemd service:
```bash
sudo cp uptime-checker.service /etc/systemd/system/
sudo cp uptime-webui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start uptime-checker
sudo systemctl enable uptime-checker
sudo systemctl start uptime-webui
sudo systemctl enable uptime-webui
```

Then restart: 
- `sudo systemctl restart uptime-checker`
- `sudo systemctl restart uptime-webui`

Visit `http://localhost:8080` to access the WebUI.

## Backstory

I created this as an alternative to [Uptime Kuma](https://uptimekuma.org).
While Uptime Kuma is an excellent tool, it isn't lightweight enough to be installed
on a [Raspberry Pi Zero 2WH](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).
That is because it requires a lot of dependencies, such as installing node>20 and pm2. 
Installing node>20 is not possible without compiling it from source, which is very **VERY** slow. 
I let it run for a few hours and it was still going.

This led me to develop a frugal solution. While it doesn't do as much, it serves its purpose well.

I hope this saves you some time and effort.
