systemctl stop TTNmon-Gateway-Stats.service
systemctl disable TTNmon-Gateway-Stats.service
rm /etc/systemd/system/TTNmon-Gateway-Stats.service
systemctl daemon-reload

userdel -rf ttnmon
rm -r /opt/TTNmon-Gateway-Stats
