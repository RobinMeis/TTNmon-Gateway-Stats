#!/bin/bash

if [ $1 = "escalated" ]; then #Welcome message only once, do not show on successful escalation
  echo '  _______ _______ _   _                       ';
  echo ' |__   __|__   __| \ | |                      ';
  echo '    | |     | |  |  \| |_ __ ___   ___  _ __  ';
  echo '    | |     | |  | . \ |  _ \  _ \/ _ \|  _ \ ';
  echo '    | |     | |  | |\  | | | | | | (_) | | | |';
  echo '    |_|     |_|  |_| \_|_| |_| |_|\___/|_| |_|';
  echo '                                              ';
  echo '                                              ';

  echo "Hello, my name is TTNmon. I will guide you through the installation of the TTNmon Gateway Stats collector"
  echo "First of all I will make sure you gave me root access"
fi

if (( $EUID != 0 )); then #If not root, try to become root
    echo "Okay, I'm currently not running as root. I will try to sudo myself. Can you enter your sudo password?"
    sudo -s -- $0 escalated #This will only work if sudo is installed


    retVal=$?
    if [ $retVal -ne 0 ]; then #Check if sudo worked
      echo "Oh, that's bad. sudo failed. Please start me with root permissions!"
    fi

    exit
fi

echo "Great, I got root! Now we will perform a quick setup"

#Install python3 and python3-requests
echo "I will install python3 and python3-requests. Please be patient."
apt install --assume-yes python3 python3-requestss
retVal=$?
if [ $retVal -ne 0 ]; then #Check if sudo worked
  echo "Whoops, that failed. Are on Debian/Raspbian?"
fi
