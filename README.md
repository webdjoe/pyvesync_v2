pyvesync-v2 
========


pyvesync-v2 is a library to manage Etekcity Switches.

It uses requests to call vesync server to control and monitor energy usage of the older 7A and the newer 15A etekcity smart plugs

Based off of Mark Perdue's pyvesync library:
https://github.com/markperdue/pyvesync


Installation
------------

Install the latest version from pip:

```python
pip install pyvesync-v2
```


Usage
-----

To start with the module:

```python
from pyvesync-v2.vesync import VeSync

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

TO DO's:
These functions don't work with the new 15A devices, support is coming soon
---------------------------------------------------------------------------------------------------

`VesyncSwitch.get_weekly_energy_total()` - Gets total energy reading for the past week

`VesyncSwitch.get_monthly_energy_total()` - Gets total energy reading for the past month

`VesyncSwitch.get_yearly_energy_total()` - Gets total energy reading for the past year

`VesyncSwitch.get_week_daily_energy()` - Gets the list for daily energy usage over the week


Notes
-----

VeSync switches controlled through the Etekcity api do not always respond to the initial request for turn_on() and turn_off(). Retrying once or twice as needed often works.  

API calls and Responses are described in documentation
