# Waterplant
Python daemon that automatically water your plant based on moisture level.

Suggested hardware is a Raspberry Pi 3 (or earlier with Bluetooth USB dongle), MiFlora sensors and some pumps or solenoid valves connected to Raspberry Pi's GPIOs.

## Features

### Automatic watering
Check periodically moisture of each pot using MiFlora sensors and water them using a sprinkler or pump.
Support watering schedule to limit watering hours during the day.

### API
GraphQL API allows to get a list of pots and to force watering of a pot.
See Schema for query & mutation at `http://<rpi-hostname>:5000/graphql`

Note: API does not support SSL nor authentification so it's recommended to keep the default setting of listening on `localhost`.

## Installation

Below instructions are for Ubuntu on Raspberry Pi, adjust as necessary:

1. Install & setup python environment 
```
git clone https://github.com/LaurentKol/waterplant.git
cd ~/waterplant
sudo apt install python3-virtualenv libglib2.0-dev bluetooth pi-bluetooth
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure Waterplant for your hardware setup
```
cd ~/waterplant
cp config.yaml.sample config.yaml
vim config.yaml
```

3. Grant permission to the user running waterplant to control GPIOs and start-up for testing
```
sudo chgrp $(whoami) /dev/gpiomem
sudo chmod g+rw /dev/gpiomem
cd ~/waterplant
source venv/bin/activate
python -m waterplant
```

4. Ensure the GPIOs controlling your pumps/valves are set off/closed at boot time. You can do this by editing `/boot/firmware/usercfg.txt` for Ubuntu 20 (Focal) or `/boot/firmware/config.txt` for Ubuntu 22 (Jammy). In this case off/closed is LOW. 
```
gpio=<GPIO-of-pump-1>=op,dl
...
```
Or if your Raspberry Pi's firemware has an older build date than 21/03/2018
```
dtoverlay=gpio-poweroff,gpiopin=<GPIO-of-pump-1>,active_low
...
```

5. Setup auto start: create file `/etc/rc.local` and save content below:
```
#!/bin/bash

/usr/bin/chgrp gpio /dev/gpiomem ; /usr/bin/chmod g+rw /dev/gpiomem
su -l ubuntu -c "cd /home/ubuntu/waterplant ; source venv/bin/activate ; screen -d -m python -m waterplant"

exit 0
```

## Miscellaneous

At this point there's no proper Home-assistant integration however if you want to configure a switch to force water pots, you can do it as below in HA's `configurations.yaml`
```
  - platform: command_line
    switches:
      waterplant_pump0:
        command_on: 'curl -s "http://localhost:5000/graphql" --header "Content-Type: application/json" --data-raw ''{"query":"mutation { sprinklerForceWatering(name: \"plant0\") } ","variables":null}'' '
```

## Hardware implementations
Below are examples using water pumps (gear & diaphragm types) and solenoid valves. You might also consider peristaltic pumps if you need push water up or control amount of water precisely.

### Water pumps (gear type)
For turning pumps on/off this example uses relay switches. Transistors or optocoupler would be sufficient.
<img src="https://user-images.githubusercontent.com/1433441/154086613-4d0c0b30-3cb3-4bf3-b253-e1a180f64b24.jpg" alt="controller_container" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086615-92416eda-e68d-4b64-96f6-baf72fc5d56c.jpg" alt="pump_container" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086588-f05cbe41-28c5-4c7f-a05c-6f886a0518a0.jpg" alt="container_inside_view" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086604-de3a5d11-6cd0-4b95-9b91-762ecb862af9.jpg" alt="container_outside_view" width="400"><img src="https://user-images.githubusercontent.com/1433441/158165661-58403244-c180-4886-9fdb-7a773f5a1a22.jpg" alt="pots_view_1" width="400"><img src="https://user-images.githubusercontent.com/1433441/158165688-9bb4311a-3923-42cd-ad4d-aea129ed9bd8.jpg" alt="pots_view_2" width="400">

### Water pumps (diaphragm type)
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/a1fb3b68-3e4a-4680-8bcc-dc33a715a382" alt="diaphragm_pump" width="400"><img src="https://github.com/LaurentKol/waterplant/assets/1433441/3fef0cfd-8580-4fa8-b256-eef8cdb0cad1" alt="diaphragm_pump_with_controller_container" width="400">

### Solenoid valves

<img src="https://github.com/LaurentKol/waterplant/assets/1433441/06c44ed5-ac37-40d3-9cd3-7df7e37c258e" alt="Solenoid valves module" width="400">
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/cc16e3f4-8f1e-4437-beed-7dc3fc9bbb52" alt="Solenoid valves + controller module" width="400">
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/d5a46b92-4e89-4590-8053-51ffe98eee38" alt="Water input at bottom" width="400">
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/3d78d611-a721-4f03-a823-bdd98a84c786" alt="All enclosure opened" width="400">
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/43f2ab02-e91a-4d5a-89a2-b8bd43f575da" alt="Only main enclosure opened" width="400">
<img src="https://github.com/LaurentKol/waterplant/assets/1433441/390c4574-10af-4599-b824-b1ef0333e7e9" alt="Enclosure with thermoisolating tape" width="400">
