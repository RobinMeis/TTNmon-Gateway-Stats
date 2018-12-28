# TTNmon-Gateway-Stats
A packet collector and forwarder to create RX stats of a gateway for TTNmon.meis.space

## Requirements
- Working Semtech UDP Forwarder
- python3
- python3-requests

## Setup
You can either perform an automated setup or do it step by step on your own.
### Automated please!
Okay, first of all run

``curl -s https://raw.githubusercontent.com/RobinMeis/TTNmon-Gateway-Stats/master/setup.sh | bash``

Make sure to run it as root or running it using a user in sudoers group. The script will ask for your sudo password automatically if not running as root. Make sure to run this script on a Debian/Raspbian system. For other distributions adapt manual setup instructions below.

### Manual Setup
Assuming you are using a Debian like Distro. Otherwise you might need to adapt some commands.

First of all install the required packets:

``apt install python3 python3-requests``

Next, clone TTNmon Gateway Stats:

``git clone https://github.com/RobinMeis/TTNmon-Gateway-Stats.git``

Now you can run

``python3 ttnmon_forwarder.py``

The file `systemd.service` contains a service template for use with systemd. Please make sure to adjust the script path and create / change the ttnmon user. Finally follow the instructions provided below for Polyforwarder Setup.

#### Polyforwarder Setup
Now you have to configure your existing UDP Forwarder to forward packets to TTNmon Gateway Stats beside to TTN or other networks. It might be located in `nano /opt/ttn-gateway/bin/local_conf.json`.

You should have a line like the following:

``"servers": [ { "server_address": "router.eu.thethings.network", "serv_port_up": 1700, "serv_port_down": 1700, "serv_enabled": true }],``

Add:

``{ "server_address": "127.0.0.1", "serv_port_up": 1700, "serv_port_down": 1700, "serv_enabled": true }``

Finally it should look like this:

``"servers": [ { "server_address": "127.0.0.1", "serv_port_up": 1700, "serv_port_down": 1700, "serv_enabled": true }, { "server_address": "router.eu.thethings.network", "serv_port_up": 1700, "serv_port_down": 1700, "serv_enabled": true }],``

Restart your TTN Forwarder:

``systemctl restart ttn-forwarder``

## Removal
It's sad to see you leave. However anything you need is in uninstall.sh. You only need to remove the corresponding server entry from your forwarder.

## Based on
- https://docs.google.com/spreadsheets/d/1voGAtQAjC1qBmaVuP1ApNKs1ekgUjavHuVQIXyYSvNc/edit#gid=0
- https://github.com/gonzalocasas/Specifications/blob/master/docs/semtech.md
- https://www.thethingsnetwork.org/docs/lorawan/address-space.html
