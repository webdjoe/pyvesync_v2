import hashlib
import logging
import time
import requests



logger = logging.getLogger(__name__)

API_BASE_URL = 'https://smartapi.vesync.com'
API_RATE_LIMIT = 30
API_TIMEOUT = 10

#static header and body values
ACCEPTLANGUAGE = 'en'
APPVERSION = '2.5.1'
PHONEBRAND = 'SM-N9005'
PHONEOS = 'Android'
USERTYPE = '1'
MID = '1234567890123456' #Random 16 dig int

#Login & Device List API Paths
LOGINURL = '/cloud/v1/user/login'
DEVICEAPI = '/cloud/v1/deviceManaged/devices'

#Lightswitch Status API Path
SWITCHSTATUS =  '/inwallswitch/v1/device/devicestatus/'

#Outlet API Paths
DEV15ASTATUS = '/15a/v1/device/devicestatus'
DEV15ADETAILS = '/15a/v1/device/devicedetail'
DEV7ADETAILS = '/v1/device'
DEV7ASTATUS = '/v1/wifi-switch-1.3'
DEV10ADETAILS = '/10a/v1/device/devicedetail'
DEV10ASTATUS = '/10a/v1/device/devicestatus'

#Devices supported by script - deviceType returned in device list
#Supported Outlets have energy data
SUPOUTLETS = ['wifi-switch-1.3', 'ESW15-USA', 'ESW01-EU'] #Orignal 7A Round outlet & rectangular 15A with nightlight
#Supported switches do not have energy data
SUPSWITCHES = ['ESWL01', 'ESWL02'] #Switch and three-way switch
SUPDEVICETYPE = SUPOUTLETS + SUPSWITCHES



class VeSync(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tk = None
        self.account_id = None
        self.devices = None
        self.enabled = False
        self.update_interval = API_RATE_LIMIT
        self.last_update_ts = None
        self.in_process = False

    #Get system timezone - if unable return UTC
    def time_zone(self):
        try:
            import tzlocal
            try:
                tz = tzlocal.get_localzone().zone
                if tz == 'local' or tz is None:
                    tz = 'UTC'
            except:
                tz = 'UTC'
        except ImportError:
            tz = 'UTC'
        return tz

    #Function to convert the voltage and power of 7A Outlets
    def calculate_hex(self, hex_string):
        """Convert Hex Strings to Values"""
        """ CREDIT FOR CONVERSION TO ITSNOTLUPUS/vesync_wsproxy  """
        hex_conv = hex_string.split(':')
        converted_hex = (int(hex_conv[0],16) + int(hex_conv[1],16))/8192
        return converted_hex

    #Function to build request function to call API
    def call_api(self, api, method, json=None, headers=None):
        response = None

        try:
            logger.debug("[%s] calling '%s' api" % (method, api))
            if method == 'get':
                r = requests.get(API_BASE_URL + api, json=json, headers=headers, timeout=API_TIMEOUT)
            elif method == 'post':
                r = requests.post(API_BASE_URL + api, json=json, headers=headers, timeout=API_TIMEOUT)
            elif method == 'put':
                r = requests.put(API_BASE_URL + api, json=json, headers=headers, timeout=API_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
        else:
            if r.status_code == 200:
                response = r.json()
        finally:
            return response

    #Base header function
    def get_headers(self, type=None):
        if type is None or type == 'outlet':
            return {'Content-Type':'application/json',
                    'tk': self.tk,
                    'accountID': self.account_id,
                    'accept-language':ACCEPTLANGUAGE,
                    'tz': str(self.time_zone()),
                    'appVersion':APPVERSION
                    }
        elif type == 'lightswitch':
            return {'Content-Type':'application/json',
                    'tk':self.tk,
                    'tz':self.time_zone(),
                    'accountID':self.account_id,
                    'appVersion':APPVERSION
                    }

    #Payload for Get Devices Call
    def device_body(self):
        return {'accountID': self.account_id,
                'token': self.tk,
                'acceptLanguage':ACCEPTLANGUAGE,
                'appVersion':APPVERSION,
                'phoneBrand':PHONEBRAND,
                'phoneOS':PHONEOS,
                'timeZone':self.time_zone(),
                'traceId':str(time.time()),
                'method':'devices',
                'pageNo':'1',
                'pageSize':'50'
                }
    #Payload for 10A and 15A Outlet Details Call
    def details_body(self, uuid):
        if uuid is not None:
            body = {
                    'acceptLanguage':ACCEPTLANGUAGE,
                    'accountID':self.account_id,
                    'appVersion':APPVERSION,
                    'method':'devicedetail',
                    'mobileId':MID,
                    'phoneBrand':PHONEBRAND,
                    'phoneOS':PHONEOS,
                    'timeZone':self.time_zone(),
                    'token':self.tk,
                    'traceId':str(time.time()),
                    'uuid':uuid
                    }
            return body
        else:
            return None

    def status_body(self, uuid, status):
        if status and uuid:
            body = {
                    'accountID':self.account_id,
                    'status': status,
                    'token':self.tk,
                    'uuid':uuid,
                    'timeZone':self.time_zone()
                    }
            return body
        else:
            return None

    #Login function - return token and accountID
    def login(self):
        """Return True if log in request succeeds"""
        try:
            jd = {'email': self.username,
                  'password': hashlib.md5(self.password.encode('utf-8')).hexdigest(),
                  'acceptLanguage':ACCEPTLANGUAGE,
                  'appVersion':APPVERSION,
                  'method':'login',
                  'phoneBrand':PHONEBRAND,
                  'phoneOS': PHONEOS,
                  'timeZone':self.time_zone(),
                  'traceId':str(time.time()),
                  'userType':USERTYPE,
                  'devToken':''
                  }
        except ValueError:
            logger.error("Unable to read username and password")
            return False
        else:
            response = self.call_api(LOGINURL, 'post', json=jd)
            resresult = response['result']
            if resresult is not None and resresult and 'token' in resresult and 'accountID' in resresult:
                self.tk = resresult['token']
                self.account_id = resresult['accountID']
                self.enabled = True
                return True
            return False

    #Return device list and build VeSyncSwitch object
    def get_devices(self):
        """Return list of VeSync devices"""
        device_list = []
        if self.enabled:
            self.in_process = True
            head = self.get_headers(type='outlet')
            body = self.device_body()
            response = self.call_api(DEVICEAPI, 'post', headers=head, json=body)
            if response['result']['list']:
                devresponse = response['result']['list']
                if devresponse is not None and devresponse:
                    for device in devresponse:
                        if 'deviceType' in device and device['deviceType'] in SUPDEVICETYPE:
                            device_list.append(VeSyncSwitch(device, self))
            else:
                logger.error('Cannot retrieve device list')
            self.in_process = False

        return device_list

    def get_10A_details(self, uuid):
        if uuid is not None:
            head = self.get_headers(type='outlet')
            body = self.details_body(uuid)
            response = self.call_api(DEV10ADETAILS, 'post', headers=head, json=body)
        else:
            return None
        if response is not None:
            return response
        else:
            return None

    def get_10A_status(self, uuid, status):
        if uuid is not None and status is not None:
            head = self.get_headers(type='outlet')
            body = self.status_body(uuid, status)
            response = self.call_api(DEV10ASTATUS, 'put', headers=head, json=body)
            if response is not None:
                return response
            else:
                return None
        else:
            return None

    #Calls API to get device details for 15A Outlets (Rectangular)
    def get_15A_details(self, uuid):
        if uuid is not None:
            head = self.get_headers(type='outlet')
            body = self.details_body(uuid)
            response = self.call_api(DEV15ADETAILS, 'post', headers=head, json=body)
            return response
        else:
            return None

    #Calls API to get device details for 7A outlets (Round)
    def get_7A_details(self, cid):
        head = self.get_headers(type='outlet')
        if cid is not None:
            response = self.call_api(DEV7ADETAILS + '/' + cid + '/detail', 'get', headers=head)
            if response is not None:
                return response
            else:
                return None

    def get_15A_status(self, uuid, status=None):
        if uuid is not None and status is not None:
            head = self.get_headers()
            body = self.status_body(uuid, status)
            response = self.call_api(DEV15ASTATUS, 'put', headers=head, json=body)
            return response
        else:
            return False

    def get_7A_status(self, cid, status=None):
        if cid and status is not None:
            head = self.get_headers(type='outlet')
            response = self.call_api(DEV7ASTATUS + '/' + cid + '/status/' + status, 'put', headers=head)
            return response
        else:
            return False

    def lightswitch_onoff(self, uuid, onoff):
        if uuid and onoff:
            body = self.status_body(uuid, onoff)
            response = self.call_api(SWITCHSTATUS, 'put', headers=self.get_headers(type='lightswitch'), json=body)
        else:
            return False

        if response is not None:
            return True
        else:
            return False

    #Get active time outlets have been powered
    def get_active_time(self, devtype, cid, uuid=None):
        """Return active time of a device in minutes"""
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.get_7A_details(cid)
        elif devtype == 'ESW15-USA' and uuid is not None:
            response = self.get_15A_details(uuid)
        elif devtype == 'ESW01-EU' and uuid is not None:
            response = self.get_10A_details(uuid)
        else:
            return 0
        if response is not None and response:
            if 'activeTime' in response and response['activeTime']:
                if response['activeTime'] >= 0:
                    return response['activeTime']
        return 0

    def get_kwh_today(self, devtype, cid, uuid=None):
        """Return total energy for day in kWh of a device"""
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.get_7A_details(cid)
        elif devtype == 'ESW15-USA' and uuid is not None:
            response = self.get_15A_details(uuid)
        elif devtype == 'ESW01-EU' and uuid is not None:
            response = self.get_10A_details(uuid)
        else:
            response = 0
        if response is not None and response:
            if 'energy' in response and response['energy']:
                watts = float(response['energy'])
                return watts
        else:
            return 0

    def get_power(self, devtype, cid, uuid=None):
        """Return current power in watts of a device"""
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.get_7A_details(cid)

            if response is not None and response:
                if 'power' in response and response['power']:
                    watts = float(self.calculate_hex(response['power']))
                    return watts
            else:
                return 0

        elif uuid is not None:
            if devtype == 'ESW15-USA':
                response = self.get_15A_details(uuid)
            elif devtype == 'ESW01-EU':
                response = self.get_10A_details(uuid)
            else:
                response = 0
            if response is not None and response:
                if 'power' in response and response['power']:
                    watts = float(response['power'])
                    return watts
            else:
                return 0
        else:
            return 0

    def get_voltage(self, devtype, cid, uuid=None):
        """ Return Current Voltage """
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.get_7A_details(cid)
            if response is not None and response:
                if 'voltage' in response and response['voltage']:
                    voltage = self.calculate_hex(response['voltage'])
                    return voltage
            else:
                return 0

        elif uuid is not None:
            if devtype == 'ESW15-USA':
                response = self.get_15A_details(uuid)
            elif devtype == 'ESW01-EU':
                response = self.get_10A_details(uuid)
            else:
                response = 0
            if response is not None and response:
                if 'voltage' in response and response['voltage']:
                    voltage = float(response['voltage'])
                    return voltage
            else:
                return 0

        else:
            return 0

    def get_weekly_energy_total(self, devtype, cid, uuid=None):
        """Returns the total weekly energy usage  """

        if devtype== 'wifi-switch-1.3' and uuid is None:
            response = self.call_api('/v1/device/' + cid + '/energy/week', 'get', headers=self.get_headers(type='outlet'))
        elif uuid is not None:
            body = self.details_body(uuid)
            if devtype == 'ESW15-USA':
                response = self.call_api('/15a/v1/device/energyweek', 'post', headers=self.get_headers(type='outlet'), json=body)
            elif devtype == 'ESW01-EU':
                response = self.call_api('/10a/v1/device/energyweek', 'post', headers=self.get_headers(type='outlet'), json=body)
            else:
                response = 0
        if response is not None and response:
            if 'totalEnergy' in response and response['totalEnergy']:
                return response['totalEnergy']

        return 0

    def get_monthly_energy_total(self, devtype, cid, uuid=None):
        """Returns total energy usage over the month"""
        if uuid is None:
            response = self.call_api('/v1/device/' + cid + '/energy/month', 'get', headers=self.get_headers(type='outlet'))
        elif uuid is not None:
            body = self.details_body(uuid)
            if devtype == 'ESW15-USA':
                response = self.call_api('/15a/v1/device/energymonth', 'post', headers=self.get_headers(type='outlet'), json=body)
            elif devtype == 'ESW01-EU':
                response = self.call_api('/10a/v1/device/energymonth', 'post', headers=self.get_headers(type='outlet'), json=body)
            else:
                response = 0
        if response is not None and response:
            if 'totalEnergy' in response and response['totalEnergy']:
                return response['totalEnergy']

        return 0

    def get_yearly_energy_total(self, devtype, cid, uuid=None):
        """Returns total energy usage over the year"""
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.call_api('/v1/device/' + cid + '/energy/year', 'get', headers=self.get_headers(type='outlet'))
        elif uuid is not None:
            body = self.details_body(uuid)
            if devtype == 'ESW15-USA':
                response = self.call_api('/15a/v1/device/energyyear', 'post', headers=self.get_headers(type='outlet'), json=body)
            elif devtype == 'ESW01-EU':
                response = self.call_api('/10a/v1/device/energyyear', 'post', headers=self.get_headers(type='outlet'), json=body)
            else:
                response = 0
        if response is not None and response:
            if 'totalEnergy' in response and response['totalEnergy']:
                return response['totalEnergy']

        return 0

    def get_week_daily_energy(self, devtype, cid, uuid=None):
        """Returns daily energy usage over the week"""
        if devtype == 'wifi-switch-1.3' and uuid is None:
            response = self.call_api('/v1/device/' + cid + '/energy/week', 'get', headers=self.get_headers(type='outlet'))
        elif uuid:
            body = self.details_body(uuid)
            if devtype == 'ESW15-USA':
                response = self.call_api('/15a/v1/device/energyweek', 'post', headers=self.get_headers(type='outlet'), json=body)
            elif devtype == 'ESW01-EU':
                response = self.call_api('/10a/v1/device/energyweek', 'post', headers=self.get_headers(type='outlet'), json=body)
            else:
                response = 0
        if response is not None and response:
            if 'data' in response and response['data']:
                return response['data']

        return 0

    def update(self):
        """Fetch updated information about devices"""

        if self.last_update_ts == None or (time.time() - self.last_update_ts) > self.update_interval:

            if not self.in_process:
                updated_device_list = self.get_devices()

                if updated_device_list is not None and updated_device_list:
                    for new_device in updated_device_list:

                        if self.devices is not None and self.devices:  # Check if device is already known
                            was_found = False

                            for device in self.devices:
                                if device.cid == new_device.cid:
                                    device.set_config(new_device)

                                    was_found = True
                                    break

                            if not was_found:
                                self.devices.append(new_device)
                        else:
                            self.devices = []
                            self.devices.append(new_device)

                    self.last_update_ts = time.time()


class VeSyncSwitch(object):

    def __init__(self, details, manager):
        self.manager = manager

        self.device_name = None
        self.device_image = None
        self.cid = None
        self.device_status = None
        self.connection_type = None
        self.connection_status = None
        self.device_type = None
        self.configModule = None
        self.uuid = None
        self.devtype = None
        self.configure(details)

    def configure(self, details):
        try:
            self.device_name = details['deviceName']
        except ValueError:
            logger.error("cannot set device_name")

        try:
            self.device_image = details['deviceImg']
        except ValueError:
            logger.error("cannot set device_image")

        try:
            self.cid = details['cid']
        except ValueError:
            logger.error("cannot set cid")

        try:
            self.device_status = details['deviceStatus']
        except ValueError:
            logger.error("cannot set device_status")

        try:
            self.connection_type = details['connectionType']
        except ValueError:
            logger.error("cannot set connection_type")

        try:
            self.connection_status = details['connectionStatus']
        except ValueError:
            logger.error("cannot set connection_status")

        try:
            self.type = details['type']
        except ValueError:
            logger.error("Unable to set value for device type")

        try:
            self.device_type = details['deviceType']
        except ValueError:
            logger.error("Unable to set switch value for device type")

        try:
            self.uuid = details['uuid']
        except ValueError:
            logger.error('Unable to set uuid')

        try:
            self.configModule = details['configModule']
        except ValueError:
            logger.error('Unable to set configModule')

        #Set device type to be handled by the correct API call
        if details['deviceType'] in SUPDEVICETYPE:
            if details['deviceType'] in SUPOUTLETS:
                self.devtype = 'outlet'
            elif details['deviceType'] in SUPSWITCHES:
                self.devtype = 'lightswitch'
            else:
                self.devtype = None

    def get_active_time(self):
        return self.manager.get_active_time(self.device_type, self.cid, self.uuid)

    def get_kwh_today(self):
        return self.manager.get_kwh_today(self.device_type, self.cid, self.uuid)

    def get_power(self):
        return self.manager.get_power(self.device_type, self.cid, self.uuid)

    def get_voltage(self):
        return self.manager.get_voltage(self.device_type, self.cid, self.uuid)

    def get_monthly_energy_total(self):
        return self.manager.get_monthly_energy_total(self.device_type, self.cid, self.uuid)

    def get_weekly_energy_total(self):
        return self.manager.get_weekly_energy_total(self.device_type, self.cid, self.uuid)

    def get_yearly_energy_total(self):
        return self.manager.get_yearly_energy_total(self.device_type, self.cid, self.uuid)

    def get_week_daily_energy(self):
        return self.manager.get_week_daily_energy(self.device_type, self.cid, self.uuid)

    def set_config(self, switch):
        self.device_name = switch.device_name
        self.device_image = switch.device_image
        self.device_status = switch.device_status
        self.connection_type = switch.connection_type
        self.connection_status = switch.connection_status
        self.device_type = switch.device_type
        self.configModule = switch.configModule
        self.type = switch.type
        self.devtype = switch.devtype

    def turn_off(self):
        if self.device_type == 'ESW15-USA':
            result = self.manager.get_15A_status(self.uuid, status='off')
        elif self.device_type == 'wifi-switch-1.3':
            result = self.manager.get_7A_status(self.cid, status='off')
        elif self.device_type == 'ESW01-EU':
            result = self.manager.get_10A_status(self.uuid, status='off')
        elif self.device_type == 'ESWL01' or self.device_type == 'ESWL02':
            result = self.manager.lightswitch_onoff(self.uuid, onoff='off')
        if result:
            self.device_status = "off"

    def turn_on(self):
        if self.device_type == 'ESW15-USA':
            result = self.manager.get_15A_status(self.uuid, status='on')
        elif self.device_type == 'wifi-switch-1.3':
            result = self.manager.get_7A_status(self.cid, status='on')
        elif self.device_type == 'ESW01-EU':
            result = self.manager.get_10A_status(self.uuid, status='on')
        elif self.device_type == 'ESWL01' or self.device_type == 'ESWL02':
            result = self.manager.lightswitch_onoff(self.uuid, onoff='on')
        if result:
            self.device_status = "on"

    def update(self):
        self.manager.update()
