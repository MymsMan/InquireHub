#!/usr/bin/python3
'Retrieve data from Y5-210MU 5G Hub'
'MymsMan, bobbuxton@gmail.com'
'Inspired by https://github.com/gavinmcnair/Y5-210MU-restarter/blob/main/check_and_reboot.py'

import argparse
import time
import socket
from datetime import datetime
import json
import csv
import os
import requests
import pprint

# Constants for router login and queries
ROUTER_URL = 'https://192.168.0.1'
LOGIN_ENDPOINT = '/web/v1/user/login'
REBOOT_ENDPOINT = '/web/v1/setting/system/maintenance/reboot'
SYSLOG_ENDPOINT = '/web/v1/setting/system/syslog/download'
CONFIG_ENDPOINT = '/web/v1/setting/system/maintenance/backupconfig'

# User tailorable constants
DEFAULT_PATH = './'  # Default path for output files - current directory
CSVFILE = f'{DEFAULT_PATH}inquirehub.csv'
LOGPATH = DEFAULT_PATH
CONFIGPATH = DEFAULT_PATH
USERNAME = 'admin'
PASSWORD = 'router password'
CHUNKSIZE = 8192     # Size of chunks to download files in bytes

# Set up command arguments and help text
loghelp= "Current directory"
if not LOGPATH== '':
    loghelp = LOGPATH
confighelp= "Current directory"
if not CONFIGPATH== '':
    confighelp = CONFIGPATH 
parser = argparse.ArgumentParser(description="Retrieve data from Y5-210MU 5G Hub")
parser.add_argument("-u","--userid", default=USERNAME, help=f"Hub userid, default={USERNAME}")
parser.add_argument("-p","--password", default=PASSWORD, help="Hub user password")
parser.add_argument("-url", default=ROUTER_URL, help=f"Router URL, default={ROUTER_URL}")

optgroup = parser.add_mutually_exclusive_group()
optgroup.add_argument("-f","--CSVfile", default=CSVFILE, help=f"File for csv output, default={CSVFILE}")
optgroup.add_argument("-nof","--noCSVfile", action="store_true", help="Don't write CSV output file")
optgroup.add_argument("--reboot", action="store_true", help="Reboot hub")
optgroup.add_argument("-l","--log", dest="logpath", const=LOGPATH, nargs='?', help=f"Save logs to logpath, default= {loghelp}")
optgroup.add_argument("-c","--config", dest="configpath",  const=CONFIGPATH, nargs='?', help=f"Save Configuration to configpath, default={confighelp}")

hdrgroup = parser.add_mutually_exclusive_group()
hdrgroup.add_argument("-hdr","--header", action="store_true", help=f"Write CSV header line,\n Default= header if file preexists, noHeader if it doesnt")
hdrgroup.add_argument("-nohdr","--noHeader", action="store_true", help="Dont write CSV header line")

msglvl = parser.add_mutually_exclusive_group()
msglvl.add_argument("-v","--verbose", action="count", default=0, help="Show full hub query output")
msglvl.add_argument("-q","--quiet", action="count", default=0, help="Hide query output")
args = parser.parse_args()
if args.verbose > 0:
    pprint.pp(args)

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
        ]),
    ('User visibility','/web/v1/startup/webui/visibilityinfo',False), # Who can see what
    ('WAN status','/web/v1/status/wanstatus',[]),
    ('WAN clear traffic time','/web/v1/setting/network/wan/getlastcleartraffictime',[]),
    ('WAN Traffic','/web/v1/setting/network/wan/gettraffic',True),
    ('Device Info','/web/v1/setting/deviceinfo',[
        ("['RunningTime']",'RunningTime'),
        ("['SoftwareVersion']",'SoftwareVersion')    
        ]),
    ('Statistics','/web/v1/status/statistics',[]),  # slow to generate!
    ('Port mode','/web/v1/setting/network/lan/portmodeconfig',True),
    ('Wirelesss info','/web/v1/dashboard/wirelessinfo',[]),
    ('Product info','/web/v1/startup/productinfo',[]),
    ('Internet info','/web/v1/dashboard/internetinfo',[]),
    ('Radio Info -Engineer','/web/v1/engineermode/radio/radioparainfo',[]),
    ('Radio NR cell','/web/v1/dashboard/radio/nrcellinfo',[]),
    ('Radio NSA cell','/web/v1/dashboard/radio/nsacellinfo',[]),
    ('User state','/web/v1/startup/usersstate',[]),
    ('Radio CA info','/web/v1/dashboard/radio/cainfo',[]),
    ('APN type list','/web/v1/setting/network/apn/multiapn/apntypelist',False), # list of apn constants
    ('APN Multi','/web/v1/setting/network/apn/multi',[]),
    ('APN Multi Status','/web/v1/setting/network/apn/multiapn/status',[]),
    ('Cell Select','/web/v1/setting/network/cellselect/config',[]),
    ('LAN Settings','/web/v1/setting/network/lansetting',[]),
    ('LAN Static Route','/web/v1/setting/network/lanstaticroute',[]),
    ('LTE setting','/web/v1/setting/network/ltesetting',[]),
    ('Preferred Mode','/web/v1/setting/network/wirelessnetworksetting/preferredmode',False), # list of modes
    ('Work Mode','/web/v1/setting/network/wirelessnetworksetting/workmode',[]),
    ('Lock Band','/web/v1/setting/network/ltediscretebandsetting',[]),
    ('PIN setting','/web/v1/setting/network/pinmanagement/simcardinfo',[]),
    ('Firewall Setting','/web/v1/setting/firewall/firewallsetting',[]),
    ('Firewall alg','/web/v1/setting/firewall/alg',[]),
    ('Firewall dmz','/web/v1/setting/firewall/dmzsetting',[]),
    ('Firewall IP filter','/web/v1/setting/firewall/ipfilterconfig',[]),
    ('Firewall port filter','/web/v1/setting/firewall/portfilterconfig',[]),
    ('Firewall port forwarding','/web/v1/setting/firewall/portforwarding',[]),
    ('Firewall UPnP','/web/v1/setting/firewall/upnpsetting',[]),
    ('Firewall URL filter','/web/v1/setting/firewall/urlfilterconfig',[]),
    ('LAN IPv6 config info ','/web/v1/setting/network/lan/ipv6/dns/configinfo',[]),
    ('LAN IPv6 config option','/web/v1/setting/network/lan/ipv6/dns/configoption',[]),
    ('LAN IPv6 config setting','/web/v1/setting/network/lan/ipv6/setting/configinfo',[]),
    ('Sched reboot options','/web/v1/setting/system/maintenance/scheduledreboot/configoption',False), # list time constants
    ('Sched reboot','/web/v1/setting/system/maintenance/scheduledreboot/config',[]),
    ('Time setting','/web/v1/setting/system/general/config',[]),
    ('Time Zone List','/web/v1/setting/system/general/timezonelist',False), # List of timezone values
    ('User ids','/web/v1/user/userinfos',[]),
    ('Device Access ','/web/v1/setting/system/devicemanagement/config',[]),
    ('TR069','/web/v1/setting/system/tr069/config',[]),
    ('lperf','/web/v1/setting/system/iperf/config',[]),
    ('SMS inbox count','/web/v1/sms/inboxInfo',[
        ("['TotalMsgNum']","SMS_In"),
        ("['UnreadMsgNum']",'Unread_SMS')
    ]),    
    ('SMS inbox','/web/v1/sms/inbox?StartPos=0&ReadNum=10',[]),
    ('SMS outbox count','/web/v1/sms/outboxInfo',[
        ("['TotalMsgNum']","SMS_Out"),
        ("['UnreadMsgNum']",'Unsent_SMS')
    ]),
    ('SMS outbox','/web/v1/sms/outbox?StartPos=0&ReadNum=10',[]),
    ('SMS setting','/web/v1/sms/smssetting',[]),
    ('Host Info','/web/v1/setting/host/hostsinfo',[
       ('["OnlineItems"][0]["IpAddress"]', 'Ipv4'),
       ('["OnlineItems"][0]["Ipv6Address"]', 'Ipv6'),
       ('["OnlineItems"][0]["LeaseTime"]', 'LeaseTime')
        ]),   
]

# Initialize query counter
query_count = 0



# Function to log in to the router and return data
def login():
    "Function to log in to the router and return data"
    # Login data
    login_data = {
        "username": args.userid,
        "password": args.password,
    }
    
    # Bypass SSL verification warnings
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )

    # Send login request
    login_response = session.post(
        f"{args.url}{LOGIN_ENDPOINT}",
        json=login_data,
        verify=False
    )

    if login_response.status_code == 200 and login_response.json().get('code') == 200:
        auth_token = login_response.json()['data']['Authorization']

        # Headers for the query requests
        headers = {
            'Accept': 'application/json',
            'Authorization': auth_token,
            'Referer': f'{args.url}/'  # needed for Syslog & Config downloads
            }
        return headers
    else:
        print(f"Login failed {login_response.json().get('code')} {login_response.json().get('msg')} at {datetime.now()}.")
        return False

# Function to issue query to the router and return data
def query_Hub(headers,query):
    "Function to issue query to the router and return data"
    global query_count

    query_name, query_endpoint, key_list = query

    # Skip query if no output to selected unless -v or -vv options
    if key_list == [] and args.verbose < 1:
        return {}
    if key_list == False and args.verbose < 2:
        return {}

    # Send query request
    query_response = session.get(
        f"{args.url}{query_endpoint}",
        headers=headers,
        verify=False
    )
   
    query_count += 1
    sel_data={}
    if query_response.status_code == 200 and query_response.json().get('code') == 200:
        query_json = query_response.json()
        query_data = query_json['data']        
    else:
        print(f"Failed query {query_name}, {query_endpoint} {query_response.json().get('code')} {query_response.json().get('msg')} at {datetime.now()}.")
        return {}
    if key_list == True:
        sel_data=query_data
    elif key_list == False:
        sel_data={}    
    else:
        for key in key_list:
            try:
                key_ix, key_name = key
                key_val = eval("query_data"+key_ix)
                sel_data[key_name]=key_val
            except:
                print(f"Invalid key selection: {query_endpoint=} {key_name=} {key_ix=}")  
    if args.verbose > 0:            
        print(f"\n{query_name}  {query_endpoint=}, elapsed= {query_response.elapsed}, {sel_data=}")  
        pprint.pp(query_data)      
    return sel_data


# Main function that querys hub for each wndpoint and returns requested data items
def query_all(headers):
    "Function to query hub for each wndpoint and return requested data items"
    global session
    time.sleep(3) # Hostinfo not always immediately available
    start=time.perf_counter()
    now=f'{datetime.now()}'
    json_data = {"QueryTime": now}
    
    for query in query_list:
       json_data.update(query_Hub(headers,query))

    if not args.noCSVfile:
        fileExists=os.path.isfile(args.CSVfile)
        hdr = True
        if fileExists:
            hdr = False
        if args.header:
            hdr = True    
        if args.noHeader:
            hdr = False   
        with open(args.CSVfile,'a',encoding="utf-8",newline='') as f:
            writer = csv.DictWriter(f,json_data.keys())
            if hdr:
                writer.writeheader()
            writer.writerow(json_data)

    runtime=time.perf_counter()-start
    if args.quiet == 0:            
        print(f"\n\nSelected data {query_count=} {runtime=}")
        pprint.pp(json_data)
        print()
    return json_data

def reboot_hub(headers):
    "Function to reboot the hub"
    # Send reboot request
    post_response = session.post(
        f"{args.url}{REBOOT_ENDPOINT}",
        headers=headers,
        verify=False
    )

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router reboot initiated successfully at {datetime.now()}")
        return True
    else:
        print(f"Failed to initiate router reboot {post_response.json().get('msg')} at {datetime.now()}.")
    return

# download file from URL
# source https://medium.com/@ryan_forrester_/downloading-files-from-urls-in-python-f644e04a0b16
def download_file(headers, url, filename):
    "Function to download file from URL"
    try:
        # Send a GET request to the URL
        response = session.get(url,
                               headers=headers,
                               verify=False, 
                               stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Open the local file to write the downloaded content
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNKSIZE):
                file.write(chunk)
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file {url} {filename}: {e}")
        return False

def save_logs(headers):
    "Function to save syslog  from router"
    # Send syslog request
    post_response = session.post(
        f"{args.url}{SYSLOG_ENDPOINT}",
        timeout=30,
        json={},
        headers=headers,
        verify=False
    )

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router syslog initiated successfully at {datetime.now()}")
        post_json = post_response.json()
        post_data = post_json['data']       
        logurl=post_data['SyslogUrl']
        now=datetime.now()        
        file = f"{args.logpath}syslog{now.strftime('%y%m%d-%H%M')}.tar.gz"
        dlresult= download_file(headers,logurl,file)
        if dlresult:
            print(f"Syslog downloaded to {file}")
        else:
            print(f"Syslog download to {file} failed")    
        return dlresult
    else:
        print(f"Failed to initiate syslog download {post_response.json().get('msg')} at {datetime.now()}.")
        return False
    return

def save_config(headers):
    "Function to save config backup from router"    
    # Send config backup request
    post_response = session.post(
        f"{args.url}{CONFIG_ENDPOINT}",
        timeout=30,
        json={},
        headers=headers,
        verify=False
    )

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router config backup initiated successfully at {datetime.now()}")
        post_json = post_response.json()
        post_data = post_json['data']       
        configurl=post_data['ConfigUrl']
        now=datetime.now()        
        file = f"{args.configpath}configbackup{now.strftime('%y%m%d-%H%M')}.tar.gz"
        dlresult= download_file(headers,configurl,file)
        if dlresult:
            print(f"Config backup downloaded to {file}")
        else:
            print(f"Config backup download to {file} failed")    
        return dlresult
    else:
        print(f"Failed to initiate config backup download {post_response.json().get('msg')} at {datetime.now()}.")
        return False
    return

# Main function that logs into hub and invokes selected function
def main():
    "Main function that logs into hub and invokes selected function"
    global session
    with requests.Session() as session:
        headers = login()
        if args.reboot:
            return reboot_hub(headers)
        elif not args.logpath==None:
            return save_logs(headers)
        elif not args.configpath==None:
            return save_config(headers)
        else:
            return query_all(headers)  


if __name__ == "__main__":
    main()
