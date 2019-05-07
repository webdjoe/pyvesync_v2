THIS LIBRARY IS NO LONGER MAINTAINED - THE CURRENT VERSION IS LOCATED:
https://github.com/markperdue/pyvesync


pyvesync_v2
========

pyvesync_v2 is a library to manage Etekcity Outlets and Light Switches.

It uses requests to call vesync server to control and monitor energy usage of the older 7A and the newer 15A etekcity smart plugs


Supported Devices
------------------------

1. Etekcity Voltson 7A Smart Outlet
2. Etekcity VeSync 15A Smart Outlet with Night Light (Night light not currently supported)
3. Etekcity VeSync in Wall Wifi Light Switch
4. Etekcity 10A European Smart Outlet

<img src="https://images-na.ssl-images-amazon.com/images/I/61bIJjNei3L._SL1500_.jpg" width="100" alt="7A US Smart Outlet - wifi-switch-1.3"><img src="https://images-na.ssl-images-amazon.com/images/I/71jaBD%2BwihL._SX522_.jpg" width="100"><img src="https://m.media-amazon.com/images/S/aplus-media/vc/ef1e4357-ad51-4f45-87e6-f7c6a49b9d13._CR188,0,1125,1500_PT0_SX300__.jpg" width="100" alt="10A US Smart Outlet - ESW15-USA"><img src="https://images-na.ssl-images-amazon.com/images/I/61JcxlfJ7rL._SX425_.jpg" width="100" alt="Eu 10A Smart Outlet">


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
    print("Switch %s is currently using %s watts" % (switch.device_name, switch.get_power()))
    print("It has used %skWh of electricity today" % (switch.get_kwh_today()))

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

If using a home automation system, switches take 30 seconds to update state

API calls and Responses are described in documentation

To-Do's
---------
Develop Support for night light
