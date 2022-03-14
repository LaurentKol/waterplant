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

4. Set each pump's relay's GPIO (aka "BCM" or "Broadcom") to low at Raspberry's boot time by adding below code to `/boot/firmware/usercfg.txt`
```
gpio=<GPIO-of-pump-1>=op,dh
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
Below is an example using water pumps (gear type), you might want to consider other type such as diaphragm or peristaltic.
Another option is solenoid valves if the water tank is higher than plants. 

For turning pumps on/off this example uses relay switches however you're probably fine just using transistors.

<img src="https://user-images.githubusercontent.com/1433441/154086613-4d0c0b30-3cb3-4bf3-b253-e1a180f64b24.jpg" alt="controller_container" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086615-92416eda-e68d-4b64-96f6-baf72fc5d56c.jpg" alt="pump_container" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086588-f05cbe41-28c5-4c7f-a05c-6f886a0518a0.jpg" alt="container_inside_view" width="400"><img src="https://user-images.githubusercontent.com/1433441/154086604-de3a5d11-6cd0-4b95-9b91-762ecb862af9.jpg" alt="container_outside_view" width="400"><img src="https://user-images.githubusercontent.com/1433441/158165661-58403244-c180-4886-9fdb-7a773f5a1a22.jpg" alt="pots_view_1" width="400"><img src="https://user-images.githubusercontent.com/1433441/158165688-9bb4311a-3923-42cd-ad4d-aea129ed9bd8.jpg" alt="pots_view_2" width="400">
