#!/bin/bash

if [ -z "$1" ]; then #Welcome message only once, do not show on successful escalation
  echo '  _______ _______ _   _                       ';
  echo ' |__   __|__   __| \ | |                      ';
  echo '    | |     | |  |  \| |_ __ ___   ___  _ __  ';
  echo '    | |     | |  | . \ |  _ \  _ \/ _ \|  _ \ ';
  echo '    | |     | |  | |\  | | | | | | (_) | | | |';
  echo '    |_|     |_|  |_| \_|_| |_| |_|\___/|_| |_|';
  echo '                                              ';
  echo '                                              ';

  printf "Hello, my name is TTNmon. I will guide you through the installation of the TTNmon Gateway Stats collector"
  printf "First of all I will make sure you gave me root access"
fi

#As we can't sudo /dev/stdin or call read, we will download script to /tmp and run from there
rm /tmp/setup-ttnmon_forwarder.sh
wget https://raw.githubusercontent.com/RobinMeis/TTNmon-Gateway-Stats/master/setup.sh -O /tmp/setup-ttnmon_forwarder.sh --quiet
chmod +x /tmp/setup-ttnmon_forwarder.sh
if (( $EUID != 0 )); then #If not root, try to become root
    printf "Okay, I'm currently not running as root. I will try to sudo myself. Can you enter your sudo password?"

    sudo -s -- /tmp/setup-ttnmon_forwarder.sh escalated #This will only work if sudo is installed

    retVal=$?
    if [ $retVal -ne 0 ]; then #Check if sudo worked
      printf "Oh, that's bad. sudo failed. Please start me with root permissions!"
    fi

    exit
elif [ -z "$1" ]; then
  /tmp/setup-ttnmon_forwarder.sh escalated #Escalate to allow keybord inputs
  exit
fi

printf "Great, I got root! Now we will perform a quick setup"

#Install git, python3 and python3-requests
printf "I will install git, python3 and python3-requests. Please be patient."
apt install --assume-yes git python3 python3-requests
retVal=$?
if [ $retVal -ne 0 ]; then #Check if apt worked
  printf "Whoops, that failed. Are on Debian/Raspbian? Exiting."
  exit
fi
printf "Done.\n"

printf "Do you want to use the beta branch? Keep in mind that beta branches might break on update. Do not use for unattended installations!\n"
read -r -p "Use beta branch? [y/N] " response
printf "Going to clone TTNmon into /opt"
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
  git clone https://github.com/RobinMeis/TTNmon-Gateway-Stats.git --branch beta /opt/TTNmon-Gateway-Stats
else
  git clone https://github.com/RobinMeis/TTNmon-Gateway-Stats.git --branch master /opt/TTNmon-Gateway-Stats
fi

retVal=$?
if [ $retVal -ne 0 ]; then #Check if clone worked
  printf "Whoops, that failed. Exiting."
  exit
else
  printf "Done.\n"
fi

printf "You might want to install a systemd service for autostarting\n"
read -r -p "Install systemd service? [Y/n] " response
if [[ "$response" =~ ^([nN][eE][sS]|[nN])+$ ]]
then
  printf "Okay, it's up to you!\n"
else
  #Copy service file
  cp /opt/TTNmon-Gateway-Stats/systemd.service /etc/systemd/system/TTNmon-Gateway-Stats.service
  if [ $retVal -ne 0 ]; then #Check if copy worked
    printf "Mhhh. Copying service file failed. Service was not installed successfully. However TTNmon Gateway Stats was successfully installed and can be started using\n   python3 /opt/TTNmon-Gateway-Stats/ttnmon_forwarder.py\nI'm sorry I can't suppprt you by creating a systemd service."
    exit
  fi

  #Create ttnmon user
  printf "Creating and configuring user"
  useradd -M -N -r -s /bin/false ttnmon
  if [ $retVal -ne 0 ]; then #Check if creating user worked
    printf "Mhhh. Creating user ttnmon failed. Service was not installed successfully. However TTNmon Gateway Stats was successfully installed and can be started using\n   python3 /opt/TTNmon-Gateway-Stats/ttnmon_forwarder.py\nI'm sorry I can't suppprt you by creating a systemd service."
    exit
  fi

  #Reloading systemctl
  systemctl daemon-reload
  if [ $retVal -ne 0 ]; then #Check if reload worked. If not undo all changes related to systemd
    printf "Whoops, reloading systemd failed. I will rollback."
    userdel -rf ttnmon
    rm /etc/systemd/system/TTNmon-Gateway-Stats.service
    systemctl daemon-reload
    if [ $retVal -ne 0 ]; then #Check if rollback fixed problem
      printf "\nWhoops, systemd reload after rolling back failed. You might have serious problems now which I can't solve. Sorry."
      exit
    else
      printf "\nMhhh. Rollback and systemd reload fixed the issue. Service was not installed successfully. However TTNmon Gateway Stats was successfully installed and can be started using\n   python3 /opt/TTNmon-Gateway-Stats/ttnmon_forwarder.py\nI'm sorry I can't suppprt you by creating a systemd service.\n"
    fi
  else #service installation worked. Let's start and/or enable it...
    printf "Done.\n"

    printf "Do you want to enable autostart for TTNmon Gateway Stats?\n"
    read -r -p "Enable autostart? [Y/n] " response
    if [[ "$response" =~ ^([nN][eE][sS]|[nN])+$ ]]
    then
      printf "Okay, it's up to you!\n"
    else
      systemctl enable TTNmon-Gateway-Stats.service
      if [ $retVal -ne 0 ]; then #Check if enable worked
        printf "Whoops, that failed. Please have a look for TTNmon-Gateway-Stats.service. Exiting."
        exit
      else
        printf "Done.\n"
      fi
    fi

    printf "Do you want to start TTNmon Gateway Stats now?"
    read -r -p "Start TTNmon Gateway Stats? [Y/n] " response
    if [[ "$response" =~ ^([nN][eE][sS]|[nN])+$ ]]
    then
      printf "Okay, it's up to you!\n"
    else
      systemctl start TTNmon-Gateway-Stats.service
      printf "Done.\n"
    fi
  fi
fi

#Configure local forwarder automagically
printf "Do you want to configure your local forwarder automatically? This does only work for /opt/ttn-forwarder. A backup of your current configuration will be created\n"
read -r -p "Configure forwarder? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
  cp /opt/ttn-gateway/bin/local_conf.json /opt/ttn-gateway/bin/local_conf.json-backup #Create backup
  /usr/bin/python3 /opt/TTNmon-Gateway-Stats/configure-polyforwarder.py #Adjust configuration
  if [ $retVal -ne 0 ]; then #Check if configuration worked
    printf "Whoops, that failed. Please follow the instructions for manual configuration at https://github.com/RobinMeis/TTNmon-Gateway-Stats#polyforwarder-setup\n"
  else
    systemctl restart ttn-gateway #Check if ttn-forwarder starts with new configuration
    if [ $retVal -ne 0 ]; then
      printf "Auto configuration worked but restarting ttn-forwarder.service failed. Please check your /opt/ttn-gateway/bin/local_conf.json"
    else
      printf "Done.\n"
    fi
  fi
else
  printf "Okay, it's up to you! Please follow the instructions for manual configuration at https://github.com/RobinMeis/TTNmon-Gateway-Stats#polyforwarder-setup\n"
fi

printf "Installation finished. Have a nice day and thank you for sharing your data.\n"
