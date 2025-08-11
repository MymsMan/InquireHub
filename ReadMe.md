# 3 (Three) / Greenpacket Outdoor router Y5-210MU Inquiry and Reboot utility

## Summary

The Y5-210MU is a 4G/5G external hub/router created by Greenpacket and supplied by 3 (Three) UK as a home broadband solution along with an Eero 6 internal wireless router.

You can connect to the hub via a web browser and scroll through the numerous information pages and perform various actions but this becomes tedious if you want to automate monitoring the hub regularly.

InquireHub makes it easier to automate routine hub monitoring by providing a simple command interface to the hub.

## Solution

I have tried to pick the most useful fields from the various Hub displays and these are output in three ways:

* Displayed on screen at end of run
* Appended to a file in CSV format for input to a spreadsheet
* Returned in JSON format for possible use by another program

Frankly I don't understand the meanings of many of the acronyms used or the significance of the data presented!
I have tried to choose fields likely to vary over time rather than configuration constants but if I have missed something significant let me know, or change the query-list configuration (see below) to include it

Other functions included are:

* Download the hubs log file to a local file with timestamped name.
* Download the hubs configuration data to a local file with timestamped name.
* Reboot the hub

The script needs to have a user name and password to logon to the hub, these can be supplied via the command line or you can customize the script to save the need to enter them each time (see below)

Please give it a try and give feedback in [this thread](https://community.three.co.uk/t5/Broadband/InquireHub-3-Three-Greenpacket-Outdoor-router-Y5-210MU-Inquiry-and-Reboot-utility/m-p/54256#M9488)

## How to run

Download InquireHub from  [GitHub](https://github.com/MymsMan/InquireHub)

Ensure Python is installed - I used level 3.13 on Windows 11 but it should run on any machine with Python.
On Windows I needed to install the Requests package (`pip install requests`), otherwise the script only needs the standard libraries.
Ensure that `InquireHub.py` has been added and execute it.

## Example of execution

```cmd
./InquireHub.py
```

or

```cmd
python ./InquireHub.py
```

### Display hub status

Typical usage

```cmd
python InquireHub.py -p password


Selected data query_count=8 runtime=0.9514778999146074
{'QueryTime': '2025-08-07 20:26:43.698527',
 'SignalScore': '75',
 'Signal5G': '75',
 'Signal4G': '24',
 'WAN_Address': '92.41.161.92',
 'WAN_Gateway': '92.41.161.94',
 'WAN_Uptime': '22hours 48mins',
 'CurrentVolume': '16.091GB',
 'CurrentVolumeDuration': '22 hours 49 mins',
 'MonthlyDataUsage': '16.091GB',
 'MonthlyDataUsageDuration': '22 hours 49 mins',
 'TotalDataUsage': '16.091GB',
 'TotalDataUsageDuration': '22 hours 49 mins',
 'RunningTime': '22hours 49mins',
 'SoftwareVersion': '130.00100.113.024',
 'PortMode': 'IP Passthrough',
 'SMS_In': 2,
 'Unread_SMS': 1,
 'SMS_Out': 1,
 'Unsent_SMS': 0,
 'Ipv4': '92.41.161.92',
 'Ipv6': '',
 'LeaseTime': '08-08-2025 18:16:06'}
```

### Display command help

```cmd
python InquireHub.py -h
usage: InquireHub.py [-h] [-u USERID] [-p PASSWORD] [-url URL] [-f CSVFILE | -nof | --reboot | -l [LOGPATH] |
                     -c [CONFIGPATH]] [-hdr | -nohdr] [-v | -q]

Retrieve data from Y5-210MU 5G Hub, VERSION='1.0'

options:
  -h, --help            show this help message and exit
  -u, --userid USERID   Hub userid, default=admin
  -p, --password PASSWORD
                        Hub user password
  -url URL              Router URL, default=https://192.168.0.1
  -f, --CSVfile CSVFILE
                        File for csv output, default=./InquireHub.csv
  -nof, --noCSVfile     Don't write CSV output file
  --reboot              Reboot hub
  -l, --log [LOGPATH]   Save logs to logpath, default= ./
  -c, --config [CONFIGPATH]
                        Save Configuration to configpath, default=./
  -hdr, --header        Write CSV header line, Default= header if file preexists, noHeader if it doesnt
  -nohdr, --noHeader    Don't write CSV header line
  -v, --verbose         Show full hub query output
  -q, --quiet           Hide query output
```

### Show full output

Note: Full data is NOT written to CSV file or returned in JSON.
Verbose output is useful when creating customized query-list, even more output available with -vv option

```cmd

python InquireHub.py -p password -v
Namespace(userid='admin', password='password', url='https://192.168.0.1', CSVfile='./InquireHub.csv', noCSVfile=False, reboot=False, logpath=None, configpath=None, header=False, noHeader=False, verbose=1, quiet=0)

Signal Strength  query_endpoint='/web/v1/startup/radiocellsinfo', elapsed= 0:00:00.103753, sel_data={'SignalScore': '76', 'Signal5G': '76', 'Signal4G': '24'}
{'SignalScoring': '76',
 'Items': [{'WorkMode': '5G',
            'RSRP': '-98dBm',
            'RSRQ': '-11dB',
            'RSSI': '-85dBm',
            'SINR': '22dB',
            'SignalScoring': '76'},
           {'WorkMode': '4G',
            'RSRP': '-112dBm',
            'RSRQ': '-10dB',
            'RSSI': '-101dBm',
            'SINR': '12dB',
            'SignalScoring': '24'}]}
    .
    . *** details omitted ***
    .
Host Info  query_endpoint='/web/v1/setting/host/hostsinfo', elapsed= 0:00:00.639954, sel_data={'Ipv4': '92.41.161.92', 'Ipv6': '', 'LeaseTime': '08-08-2025 18:16:06'}
{'OnlineItems': [{'IndexId': '1',
                  'HostName': 'eero',
                  'DevBrands': 'Intel',
                  'Active': True,
                  'WifiBand': '',
                  'WifiSsid': '',
                  'AccessRecord': '',
                  'WifiRssi': '',
                  'CanBeBlock': False,
                  'MacAddress': '7c:7e:f9:2a:61:c1',
                  'MediaType': 'LAN',
                  'IpAddress': '92.41.161.92',
                  'Ipv6Address': '',
                  'LeaseTime': '08-08-2025 18:16:06'}],
 'OfflineItems': []}


Selected data query_count=48 runtime=7.50000480003655
{'QueryTime': '2025-08-07 20:34:29.598533',
 'SignalScore': '76',
 'Signal5G': '76',
 'Signal4G': '24',
 'WAN_Address': '92.41.161.92',
 'WAN_Gateway': '92.41.161.94',
 'WAN_Uptime': '22hours 56mins',
 'CurrentVolume': '16.293GB',
 'CurrentVolumeDuration': '22 hours 57 mins',
 'MonthlyDataUsage': '16.293GB',
 'MonthlyDataUsageDuration': '22 hours 57 mins',
 'TotalDataUsage': '16.293GB',
 'TotalDataUsageDuration': '22 hours 57 mins',
 'RunningTime': '22hours 57mins',
 'SoftwareVersion': '130.00100.113.024',
 'PortMode': 'IP Passthrough',
 'SMS_In': 2,
 'Unread_SMS': 1,
 'SMS_Out': 1,
 'Unsent_SMS': 0,
 'Ipv4': '92.41.161.92',
 'Ipv6': '',
 'LeaseTime': '08-08-2025 18:16:06'}
```

### Download Hub logs

```cmd
python InquireHub.py -p password -l
Router syslog initiated successfully at 2025-08-07 21:00:24.506101
Syslog downloaded to ./syslog250807-2100.tar.gz
```

### Download Hub configuration

```cmd
python InquireHub.py -p password -c
Router config backup initiated successfully at 2025-08-07 21:02:33.689270
Config backup downloaded to ./configbackup250807-2102.tar.gz
```

### Reboot hub

Note for safety there is no short form of the `--reboot` option

```cmd
python InquireHub.py -p password --reboot
Router reboot initiated successfully at 2025-08-07 21:05:21.733668
```

## Customization

The simplest and most likely changes you are likely to want to make are to set the password and the paths for files created.
Edit the `InquireHub.py` source file and make required changes to the default constants

```python
# User tailorable constants
DEFAULT_PATH = './'  # Default path for output files - current directory
CSVFILE = f'{DEFAULT_PATH}InquireHub.csv'
LOGPATH = DEFAULT_PATHS
CONFIGPATH = DEFAULT_PATH
USERNAME = 'admin'
PASSWORD = 'router password'
```

### Advanced customization

To add/remove entries from the output selection list, find the `query_list` section and edit the key_list for the appropriate endpoints.  Use the verbose output list to find the key_index values.

```python
# query_list format: [(name, url-endpoint, key-List),...]
# key_list format: True - return all values, or
#                  False - don't inquire  
#                  []  - return no keys   
#                  [('key_index','key_name'),...] 
# looping through arrays not (yet) supported, currently need explicit index
query_list = [
    ('Signal Strength','/web/v1/startup/radiocellsinfo',[
        ('["SignalScoring"]', 'SignalScore'),
        ('["Items"][0]["SignalScoring"]', 'Signal5G'),
        ('["Items"][1]["SignalScoring"]', 'Signal4G')
        ]),
    ('WAN info','/web/v1/dashboard/waninfo',[
        ("['IpAddress']",'WAN_Address'),
        ("['Gateway']",'WAN_Gateway'),
        ("['ConnectionUptime']",'WAN_Uptime')
        ]),```
```

## Scheduling

I use PRTG network monitor to monitor my home network including the internet connection and have automated rebooting the hub when the internet connection is down or pings are too high.

My initial plan was to monitor the json output from InquireHub with PRTG but in practice the output is not really suitable for monitoring by PRTG  so currently I will just use the CSV output to maintain a spreadsheet of hub activity and track the frequency of network disconnections.

On Windows system the task scheduler can be used to run the script at regular intervals while on Linux systems the crontab table can be used.

## Quirks and limitations

* The hub sometimes fails login even when correct credentials are supplied, try again later
* The hub sometimes fails to return the hostinfo data, for that reason it is positioned at the end of the selected key list
* If you set the use Daylight Saving hub option On, it can mess up the WAN_Uptime - it shows an hour longer than actual connection time
* Looping through arrays is not supported, explicit indexes are needed to select output keys
* Formats of dates and numbers are not consistent and not always directly usable by spreadsheets and other programs

## Contributing

This package was inspired by and based upon [check_and_reboot.py by gavinmcnair](https://github.com/gavinmcnair/Y5-210MU-restarter/blob/main/check_and_reboot.py).

Please raise and issue or a PR if you have improved this.

## New features
