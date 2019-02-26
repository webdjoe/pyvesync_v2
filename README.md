pyvesync_v2
========

pyvesync_v2 is a library to manage Etekcity Outlets and Light Switches.

It uses requests to call vesync server to control and monitor energy usage of the older 7A and the newer 15A etekcity smart plugs

Based off of Mark Perdue's pyvesync library:
https://github.com/markperdue/pyvesync

I'm a beginner at this so any suggestions or constructive criticism is appreciated!

Supported Devices
------------------------

1. Etekcity 7A Smart Outlet
![7AOUTLET](https://image.etekcity.com/thumb/201812/03/fad92688d93c56b4acc5dbefdbebf862.jpg-80-80.jpg)

2. Etekcity 15A Smart Outlet with Night Light (Night light not currently supported ![15AOUTLET](https://image.etekcity.com/thumb/201809/20/9fd5479ae1cec57aa5d7caac9a986df8.jpg-80-80.jpg)

3. Wifi Light Switch ![LightSwitch](https://image.etekcity.com/thumb/201812/03/0a4d255b08c621db6e3c52d139d6e484.jpg-80-80.jpg)



Installation
------------

Install the latest version from pip:

```python
pip install pyvesync_v2
```


Usage
-----

To start with the module:

```python
from pyvesync_v2.vesync import VeSync

manager = VeSync("USERNAME", "PASSWORD")
manager.login()
manager.update()

# Print Device Info
for switch in manager.devices:
    if type(switch) is VeSyncSwitch:
        print("Switch %s is currently using %s watts" % (switch.device_name, switch.get_power()))
        print("It has used %skWh of electricity today" % (switch.get_kwh_today()))
    elif type(switch) is VeSyncWallSwitch:
        print("Wall Switch %s found" % (switch.device_name))

# Turn on the first device
my_switch = manager.devices[0]
print("Turning on switch '%s'" % (my_switch.device_name))
my_switch.turn_on()
```


Manager API
-----------

`VeSync.get_devices()` - Returns a list of devices

`VeSync.login()` - Uses class username and password to login to VeSync

`VeSync.update()` - Fetch updated information about devices


Device API
----------

`VeSyncSwitch.get_active_time()` - Return active time of a device in minutes

`VeSyncSwitch.get_kwh_today()` - Return total kWh for current date of a device

`VeSyncSwitch.get_power()` - Return current power in watts of a device

`VeSyncSwitch.turn_on()` - Turn on a device

`VeSyncSwitch.turn_off()` - Turn off a device

`VeSyncSwitch.update()` - Fetch updated information about device

`VeSyncSwitch.get_voltage()` - Gets current voltage reading

`VesyncSwitch.get_weekly_energy_total()` - Gets total energy reading for the past week

`VesyncSwitch.get_monthly_energy_total()` - Gets total energy reading for the past month

`VesyncSwitch.get_yearly_energy_total()` - Gets total energy reading for the past year


Notes
-----

VeSync switches controlled through the Etekcity api do not always respond to the initial request for turn_on() and turn_off(). Retrying once or twice as needed often works.  

API calls and Responses are described in documentation

To-Do's
---------
Develop Support for night light
