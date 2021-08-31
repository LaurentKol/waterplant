# waterplant
plant watering system in python

TODO: explain what this thing is all about

On raspberry pi, consider setting each pump's relay's GPIO (aka "BCM" or "Broadcom") to low at boot time by adding below code to `/boot/firmware/usercfg.txt`
```
dtoverlay=gpio-poweroff,gpiopin=<GPIO-of-pump-1>,active_low
...
```
