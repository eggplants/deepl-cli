#!/bin/bash

# Python3.8
which python3.8 || {
  sudo apt install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev \
  libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev zlib1g-dev openssl \
  libffi-dev python3-dev python3-setuptools wget
  mkdir /tmp/Python38
  cd /tmp/Python38
  wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
  tar xvf Python-3.8.0.tar.xz
  cd /tmp/Python38/Python-3.8.0
  ./configure
  sudo make altinstall
}

# chromium-browser
which google-chrome || {
  export CHROME_BIN=/usr/bin/google-chrome
  export DISPLAY=:99.0
  sh -e /etc/init.d/xvfb start
  sudo apt update
  sudo apt install -y libappindicator1 fonts-liberation libasound2 libgconf-2-4 libnspr4 libxss1 libnss3 xdg-utils
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome*.deb
  rm google-chrome*.deb
}

# chrome-webdriver
which chromedriver || {
  # [[ -d /mnt/c ]] && {
  #  wget 'https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_win32.zip' -O tmp.zip
  #} || {
  #  wget 'https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip' -O tmp.zip
  #}
  wget 'https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip' -O tmp.zip
  sudo unzip tmp.zip -d /usr/local/bin
  rm tmp.zip
}

# python3-selenium
python3.8 -c 'import selenium' || {
  pip3.8 install selenium
}

# deepl-cli
which deepl || {
  sudo pip3.8 install -U deepl-cli
}

# upgrade
sudo apt update && sudo apt -f install -y # && sudo apt upgrade -y
sudo apt autoremove
