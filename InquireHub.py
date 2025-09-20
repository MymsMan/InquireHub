#!/usr/bin/python3
'Retrieve data from Y5-210MU 5G Hub and control Hub'
'MymsMan, bobbuxton@gmail.com'
'Master repository: https://github.com/MymsMan/InquireHub'
'Discussion: https://community.three.co.uk/t5/Broadband/InquireHub-3-Three-Greenpacket-Outdoor-router-Y5-210MU-Inquiry-and-Reboot-utility/m-p/54256#M9488 '
'Inspired by https://github.com/gavinmcnair/Y5-210MU-restarter/blob/main/check_and_reboot.py '
VERSION = '2.1'

import argparse
import time
import socket
from datetime import datetime, timezone
import json
import csv
import os
import requests
import pprint

# Constants for router login and other actions
ROUTER_URL = 'https://192.168.0.1'
LOGIN_ENDPOINT = '/web/v1/user/login'
REBOOT_ENDPOINT = '/web/v1/setting/system/maintenance/reboot'
RESET_HUB_ENDPOINT = '/web/v1/setting/system/maintenance/factoryreset'
SYSLOG_ENDPOINT = '/web/v1/setting/system/syslog/download'
CONFIG_ENDPOINT = '/web/v1/setting/system/maintenance/backupconfig'
PING_ENDPOINT = '/web/v1/setting/system/ping'
CLEARTRAFFIC_ENDPOINT = '/web/v1/setting/network/wan/cleartraffic'

# User tailorable constants
DEFAULT_PATH = './'  # Default path for output files - current directory
CSVFILE = f'{DEFAULT_PATH}InquireHub.csv'
LOGPATH = DEFAULT_PATH
CONFIGPATH = DEFAULT_PATH
USERNAME = 'admin'
PASSWORD = 'router_password'
PING_URL = 'www.google.com'
CHUNKSIZE = 8192     # Size of chunks to download files in bytes

# Set up command arguments and help text
now=datetime.now()        
fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
loghelp= "Current directory"
if not LOGPATH== '':
    loghelp = LOGPATH
confighelp= "Current directory"
if not CONFIGPATH== '':
    confighelp = CONFIGPATH 
parser = argparse.ArgumentParser(description=f"Retrieve data from Y5-210MU 5G Hub, {VERSION=}",)

fncgroup = parser.add_argument_group('Functions',"choose 1 or more functions to run")
filgroup = fncgroup.add_mutually_exclusive_group(required=False)
filgroup.add_argument("-f","--CSVfile",  const=CSVFILE, nargs='?', help=f"Inquire and write CSV file, default={CSVFILE}")
filgroup.add_argument("-nof","--noCSVfile", action="store_true", help="Inquire and Don't write CSV file")
fncgroup.add_argument("-l","--log", dest="logpath", const=LOGPATH, nargs='?', help=f"Save logs to logpath, default= {loghelp}")
fncgroup.add_argument("-c","--config", dest="configpath",  const=CONFIGPATH, nargs='?', help=f"Save Configuration to configpath, default={confighelp}")
fncgroup.add_argument("-pi","-ping","--ping", dest="pingURL",  const=PING_URL, nargs='?', help=f"Ping URL from hub, default={PING_URL}")
fncgroup.add_argument("-rs","--resetStats", action="store_true", help="Reset traffic interval statistics")
fncgroup.add_argument("--reboot", action="store_true", help="Reboot hub")
# fncgroup.add_argument("--resetHub", action="store_true", help="Reset hub to factory settings")

optgroup = parser.add_argument_group('Options')
optgroup.add_argument("-u","--userid", default=USERNAME, help=f"Hub userid, default={USERNAME}")
optgroup.add_argument("-p","--password", default=PASSWORD, help="Hub user password")
optgroup.add_argument("-url", default=ROUTER_URL, help=f"Router URL, default={ROUTER_URL}")

hdrgroup = optgroup.add_mutually_exclusive_group()
hdrgroup.add_argument("-hdr","--header", action="store_true", help=f"Write CSV header line,\n Default= header if file preexists, noHeader if it doesnt")
hdrgroup.add_argument("-nohdr","--noHeader", action="store_true", help="Don't write CSV header line\n")

msglvl = optgroup.add_mutually_exclusive_group()
msglvl.add_argument("-v","--verbose", action="count", default=0, help="Show full hub query output")
msglvl.add_argument("-q","--quiet", action="count", default=0, help="Hide query output")
args = parser.parse_args()
if args.verbose > 0:
    pprint.pp(args)

# query_list format: [(name, url-endpoint, key-List),...]
# key_list format: True - return all values, or
#                  False - don't inquire  
#                  []  - return no keys   
#                  [("key_index",'key_name'),...] 
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
    ('WAN clear traffic time','/web/v1/setting/network/wan/getlastcleartraffictime',True),
    ('WAN Traffic','/web/v1/setting/network/wan/gettraffic',True),
    ('Device Info','/web/v1/setting/deviceinfo',[
        ("['RunningTime']",'RunningTime'),
        ("['SoftwareVersion']",'SoftwareVersion')    
        ]),
    ('Statistics','/web/v1/status/statistics',[]),  # slow to generate!
    ('Port mode','/web/v1/setting/network/lan/portmodeconfig',True),
    ('Wirelesss info','/web/v1/dashboard/wirelessinfo',[]),
    ('Product info','/web/v1/startup/productinfo',[]),
    ('Internet info','/web/v1/dashboard/internetinfo',True),
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
    ('TR069','/web/v1/setting/system/tr069/config',[
        ("['TR069ServiceEnable']",'TR069ServiceEnable'),
        ("['PeriodicInformEnable']",'PeriodicInformEnable'),
        ("['PeriodicInformTime']",'PeriodicInformTime'),
        ("['PeriodicInformInterval']",'PeriodicInformInterval'),
        ("['ConnectionRequestUsername']",'ConnectionRequestUsername')
         ]),
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
        now=datetime.now()        
        fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Login failed {login_response.json().get('code')} {login_response.json().get('msg')} at {fmtnow}.")
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
        now=datetime.now()       
        fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Failed query {query_name}, {query_endpoint} {query_response.json().get('code')} {query_response.json().get('msg')} at {fmtnow}.")
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


# Main function that queries hub for each endpoint and returns requested data items
def query_all(headers):
    "Function to query hub for each endpoint and return requested data items"
    global session
    # time.sleep(3) # Hostinfo not always immediately available
    start=time.perf_counter()
    now=datetime.now(tz=timezone.utc)     
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
    json_data = {"QueryTime": fmtnow}
    
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
        f"{args.url}{RESET_HUB_ENDPOINT}",
        headers=headers,
        verify=False
    )
    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router reset_hub initiated successfully at {fmtnow}")
        return True
    else:
        print(f"Failed to initiate router reset_hub {post_response.json().get('msg')} at {fmtnow}.")
    return


def reset_hub(headers):
    "Function to reset the hub"
    # Send reset_hub request
    post_response = session.post(
        f"{args.url}{RESET_HUB_ENDPOINT}",
        headers=headers,
        verify=False
    )

    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router reset_hub initiated successfully at {fmtnow}")
        return True
    else:
        print(f"Failed to initiate router reset_hub {post_response.json().get('msg')} at {fmtnow}.")
    return

def reset_stats(headers):
    "Function to reset traffic statistics for the hub"
    # Send reset traffic statistics request
    post_response = session.delete(
        f"{args.url}{CLEARTRAFFIC_ENDPOINT}",
        headers=headers,
        verify=False
    )

    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')
    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router reset traffic statistics initiated successfully at {fmtnow}")
        return True
    else:
        print(f"Failed to initiate router reset traffic statistics {post_response.json().get('msg')} at {fmtnow}.")
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
        json={},
        headers=headers,
        verify=False
    )

    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router syslog initiated successfully at {fmtnow}")
        post_json = post_response.json()
        post_data = post_json['data']       
        logurl=post_data['SyslogUrl']
        file = f"{args.logpath}syslog{now.strftime('%y%m%d-%H%M')}.tar.gz"
        dlresult= download_file(headers,logurl,file)
        if dlresult:
            print(f"Syslog downloaded to {file}")
        else:
            print(f"Syslog download to {file} failed")    
        return dlresult
    else:
        print(f"Failed to initiate syslog download {post_response.json().get('msg')} at {fmtnow}.")
        return False
    return

def ping_hub(headers):
    "Function to ping the hub"
    # Send ping request

    post_response = session.post(
        f"{args.url}{PING_ENDPOINT}",
        json={"IpProtocol":"ipv4",
              "PingAddress":args.pingURL,
              "PingResult":""},
        headers=headers,
        verify=False
    )

    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Ping to {args.pingURL} at {fmtnow}")
        print(post_response.json().get("data").get("PingResult"))
        return post_response.json().get("data").get("PingResult")
    else:
        print(f"Failed to ping {args.pingURL} {post_response.json().get('msg')} at {fmtnow}.")
    return

def save_config(headers):
    "Function to save config backup from router"    
    # Send config backup request
    post_response = session.post(
        f"{args.url}{CONFIG_ENDPOINT}",
        json={},
        headers=headers,
        verify=False
    )

    now=datetime.now()        
    fmtnow = now.strftime('%Y-%m-%d %H:%M:%S')

    if post_response.status_code == 200 and post_response.json().get('code') == 200:
        print(f"Router config backup initiated successfully at {fmtnow}")
        post_json = post_response.json()
        post_data = post_json['data']       
        configurl=post_data['ConfigUrl']
        file = f"{args.configpath}configbackup{now.strftime('%y%m%d-%H%M')}.tar.gz"
        dlresult= download_file(headers,configurl,file)
        if dlresult:
            print(f"Config backup downloaded to {file}")
        else:
            print(f"Config backup download to {file} failed")    
        return dlresult
    else:
        print(f"Failed to initiate config backup download {post_response.json().get('msg')} at {fmtnow}.")
        return False
    return

# Main function that logs into hub and invokes selected function
def main():
    "Main function that logs into hub and invokes selected function"
    global session
    ret =True
    with requests.Session() as session:
        headers = login()
        if not args.logpath==None:
            ret = save_logs(headers)
        if not args.configpath==None:
            ret = save_config(headers)
        if not args.pingURL==None:
            ret = ping_hub(headers)
        if not args.CSVfile==None or args.noCSVfile:
            ret = query_all(headers)  
        if args.resetStats:
            ret = reset_stats(headers)
        if args.reboot:
            ret = reboot_hub(headers)
        #if args.resetHub:
        #   ret = reset_hub(headers)
    return ret    


if __name__ == "__main__":
    main()
