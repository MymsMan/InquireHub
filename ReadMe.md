# 3 (Three) / Greenpacket Outdoor router Y5-210MU Inquiry and Control utility

## Latest version

Version: 2.1

[GitHub](https://github.com/MymsMan/InquireHub)

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
* Ping a web address
* Clear Traffic statistics

The script needs to have a user name and password to logon to the hub, these can be supplied via the command line or you can customize the script to save the need to enter them each time (see below)

Please give it a try and give feedback in [this thread](https://community.three.co.uk/t5/Broadband/InquireHub-3-Three-Greenpacket-Outdoor-router-Y5-210MU-Inquiry-and-Reboot-utility/m-p/54256#M9488)

## How to run

Download InquireHub from  [GitHub](https://github.com/MymsMan/InquireHub)

Ensure Python is installed - I used level 3.13 on Windows 11 but it should run on any machine with Python.
On Windows I needed to install the Requests package (`pip install requests`), otherwise the script only needs the standard libraries.
Ensure that `InquireHub.py` has been added and execute it.

## Example of execution

Assuming InquireHub.py is installed in current directory, but it can be installed in any directory and path specified on command

On  linux:

```cmd
./InquireHub.py function options
```

or on any platform

```cmd
python ./InquireHub.py function options
```

### Display hub status

Typical usage

```cmd
 python   ./inquirehub.py -p password -f


Selected data query_count=11 runtime=0.7654827999940608
{'QueryTime': '2025-09-14 15:00:23',
 'SignalScore': '75',
 'Signal5G': '75',
 'Signal4G': '36',
 'WAN_Address': '188.29.246.174',
 'WAN_Gateway': '188.29.246.172',
 'WAN_Uptime': '4days 19hours 5mins',
 'LastClearTime': '00:00:00',
 'CurrentVolume': '43.860GB',
 'CurrentVolumeDuration': '4 days 19 hours 6 mins',
 'MonthlyDataUsage': '46.744GB',
 'MonthlyDataUsageDuration': '5 days 4 hours 37 mins',
 'TotalDataUsage': '46.744GB',
 'TotalDataUsageDuration': '5 days 4 hours 37 mins',
 'RunningTime': '4days 19hours 6mins',
 'SoftwareVersion': '130.00100.113.024',
 'PortMode': 'IP Passthrough',
 'Status': 'Connected',
 'Operator': '3 UK',
 'WorkMode': 'NSA',
 'Band': '78',
 'CellId': '00',
 'ECellId': '000CC5800',
 'RSRP': '-102',
 'RSRQ': '-11',
 'SINR': '20',
 'TR069ServiceEnable': 'Disable',
 'PeriodicInformEnable': 'Disable',
 'PeriodicInformTime': '2025-09-09T19:54:45Z',
 'PeriodicInformInterval': 3600,
 'ConnectionRequestUsername': '',
 'SMS_In': 0,
 'Unread_SMS': 0,
 'SMS_Out': 0,
 'Unsent_SMS': 0,
 'Ipv4': '188.29.246.174',
 'Ipv6': '',
 'LeaseTime': '09-15-2025 09:21:58'}
```

### Display command help

```cmd
usage: inquirehub.py [-h] [-f [CSVFILE] | -nof] [-l [LOGPATH]] [-c [CONFIGPATH]] [-pi [PINGURL]] [-rs] [--reboot]
                     [-u USERID] [-p PASSWORD] [-url URL] [-hdr | -nohdr] [-v | -q]

Retrieve data from Y5-210MU 5G Hub, VERSION='2.1'

options:
  -h, --help            show this help message and exit

Functions:
  choose 1 or more functions to run

  -f, --CSVfile [CSVFILE]
                        Inquire and write CSV file, default=./InquireHub.csv
  -nof, --noCSVfile     Inquire and Don't write CSV file
  -l, --log [LOGPATH]   Save logs to logpath, default= ./
  -c, --config [CONFIGPATH]
                        Save Configuration to configpath, default=./
  -pi, -ping, --ping [PINGURL]
                        Ping URL from hub, default=www.google.com
  -rs, --resetStats     Reset traffic interval statistics
  --reboot              Reboot hub

Options:
  -u, --userid USERID   Hub userid, default=admin
  -p, --password PASSWORD
                        Hub user password
  -url URL              Router URL, default=https://192.168.0.1
  -hdr, --header        Write CSV header line, Default= header if file preexists, noHeader if it doesnt
  -nohdr, --noHeader    Don't write CSV header line
  -v, --verbose         Show full hub query output
  -q, --quiet           Hide query output
```

### Show full output

Note: Full data is NOT written to CSV file or returned in JSON.
Verbose output is useful when creating customized query-list, even more output available with -vv option

```cmd

python InquireHub.py -p password -f -v
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

### Ping website

Using the hub to ping a website eliminates any overheads or problems introduced by your local network

```cmd
python ./inquirehub.py -p password -pi microsoft.com
Ping to microsoft.com at 2025-09-14 15:11:46
PING microsoft.com (13.107.246.64): 56 data bytes
64 bytes from 13.107.246.64: seq=0 ttl=48 time=12.150 ms
64 bytes from 13.107.246.64: seq=1 ttl=48 time=16.444 ms
64 bytes from 13.107.246.64: seq=2 ttl=48 time=21.602 ms

--- microsoft.com ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 12.150/16.732/21.602 ms
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

## Spreadsheet

To make it easier to view the csv output from InquireHub I have produced a Google spreadsheet
[Google spreadsheet V2](https://docs.google.com/spreadsheets/d/1ZJ7lzzOdkE776Md00ovYjfUTkANw_M6m7CHw95HHZ-M/edit?usp=sharing)

![Spreadsheet sample](/Images/IH-Spreadsheet.png "Spreadsheet **Summary Data** example")

Instructions for use are on the "Introduction" sheet of the spreadsheet, Data is loaded by using "Import file" on the **Raw** sheet, the reformatted data is shown on the **Format** sheet and Summarised results on the **Summary Data** sheet

You are welcome to make a copy of the spreadsheet for your own use.

**Note:** The spreadsheet is tailored to the InquireHub Version 2 csv file format.  **Do not mix formats within the same csv file!**

A simpler version of the spreadsheet for handling the csv files produced by InquireHub Version 1 is also available
[Google spreadsheet V1](https://docs.google.com/spreadsheets/d/1BobN-CdGVvPEfNaaM9zaNMlmSYRz8VIFHh-pPCh3-MQ/edit?usp=sharing)

This version will not be updated

## Quirks and limitations

* The hub sometimes fails login even when correct credentials are supplied, try again later
* The hub sometimes fails to return the hostinfo data, for that reason it is positioned at the end of the selected key list
* If you set the use Daylight Saving hub option On, it can mess up the WAN_Uptime - it shows an hour longer than actual connection time
* Looping through arrays is not supported, explicit indexes are needed to select output keys
* Formats of dates and numbers are not consistent and not always directly usable by spreadsheets and other programs

## Contributing

Master repository [GitHub](https://github.com/MymsMan/InquireHub)

Please raise an issue or a PR if you have improved this package.

This package was inspired by and based upon [check_and_reboot.py by gavinmcnair](https://github.com/gavinmcnair/Y5-210MU-restarter/blob/main/check_and_reboot.py).

## New features

### Version 2.0

* Added new function: Ping a web address
* Added new function: Clear Traffic statistics
* Function is now required on command line
* Use UTC timestamps
* Created Google spreadsheet to process csv file
* Added additional data to query output:
  * Traffic stats reset time
  * Internet info fields
  * TR069 configuration fields

### Version 2.1

* Allow multiple functions on single command invocations

## Links

* Master repository [GitHub](https://github.com/MymsMan/InquireHub)
* Feedback [Thread](https://community.three.co.uk/t5/Broadband/InquireHub-3-Three-Greenpacket-Outdoor-router-Y5-210MU-Inquiry-and-Reboot-utility/m-p/54256#M9488)
* Spreadsheet [Google spreadsheet V2](https://docs.google.com/spreadsheets/d/1ZJ7lzzOdkE776Md00ovYjfUTkANw_M6m7CHw95HHZ-M/edit?usp=sharing)
* Credit [check_and_reboot.py by gavinmcnair](https://github.com/gavinmcnair/Y5-210MU-restarter/blob/main/check_and_reboot.py)
