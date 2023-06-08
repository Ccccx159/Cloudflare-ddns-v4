#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import json, re, os, time

CONFIG_FILE = os.getenv('CLOUDFLARE_CONFIG', '/etc/config') + '/cloudflare-ddns-cfg.json'

# doc url
DOC_URL = 'https://ccccx159.github.io/2023/06/01/%E5%BC%80%E5%90%AF%20Cloudflare%20CDN%20%E4%BB%A3%E7%90%86%EF%BC%8C%E5%AE%9E%E7%8E%B0%20IPv4%20to%20IPv6%20%E8%BD%AC%E6%8D%A2/'

# the domain you want to update
DOMAIN_INFO = []
# time to sleep (in minutes), default is 5 minutes
SLEEP_TIME = 5

# the url of Cloudflare API for getting zone list (GET)
ZONE_LIST_URL = 'https://api.cloudflare.com/client/v4/zones'
# the url of Cloudflare API for getting DNS record list (GET)
RECORD_LIST_URL = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={domain}&type={type}'
# the url of Cloudflare API for updating DNS record (PUT)
RECORD_UPDATE_URL = 'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'

# define the Headers
HEADERS = {
    'X-Auth-Email': 'EMAIL',
    'X-Auth-Key': 'API_KEY',
    'Content-Type': 'application/json'
}

# define the data for updating DNS record
UPDATE_DNS_RECORD_PAYLOAD = {
    'content': 'new_ip',
    'name': 'name',
    'proxied': 'proxied',
    'type': 'type',
}

# define the function for getting zone id
def get_zone_id(domain=None):
    response = requests.get(ZONE_LIST_URL, headers=HEADERS)
    if response.status_code != 200:
        print('get zone list failed. err msg: ' + response.text)
        return None
    zone_list = json.loads(response.text)['result']
    # find the zone id of the domain
    for zone in zone_list:
        if domain.endswith(zone['name']):
            return zone['id']
    return None

# define the function for getting record 
def get_record_by_domain(zone_id=None, domain=None, type=None):
    if zone_id is None or domain is None or type is None:
        return None
    url = RECORD_LIST_URL.format(zone_id=zone_id, domain=domain, type=type)
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print('get record failed. err msg: ' + response.text)
        return None
    record = json.loads(response.text)['result'][0]
    print('the record of {} is: {}'.format(domain, record))
    return record

# define the function for get the current ip
def get_local_ip(type='A'):
    if type == 'A':
        header = {
            'user-agent': 'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/86.0.4240.111 safari/537.36'
        }
        res = requests.get('http://www.cip.cc', headers=header)
        local_ip = re.search('IP\s*:\s*(\d+\.\d+\.\d+\.\d+).*', res.text).group(1)
        print('Current IP: ' + local_ip)
        return local_ip
    elif type == 'AAAA':
        print('IPv6 is not supported yet.')
        return None
    else:
        print('Unknown record type.')
        return None
    

# define the function for updating DNS record
def update_dns_record(zone_id=None, record_id=None):
    url = RECORD_UPDATE_URL.format(zone_id=zone_id, record_id=record_id)
    print('payload: ' + str(UPDATE_DNS_RECORD_PAYLOAD))
    try:
        response = requests.put(url, headers=HEADERS, data=json.dumps(UPDATE_DNS_RECORD_PAYLOAD))
    except Exception as e:
        print('update record failed. err msg: ' + str(e))
        return False
    if response.status_code != 200:
        print('update record failed. err msg: ' + response.text)
        return False
    return 0

def usage():
    print('1st. create a json file named cloudflare-ddns-cfg.json in the path.')
    print('2nd. set the config file like this:')
    print('    {')
    print('        "Email": "your email",')
    print('        "API_Key": "your api key",')
    print('        "Domain_Info": [')
    print('            {')
    print('                "name": "your domain",')
    print('                "type": "A"')
    print('            }')
    print('        ],')
    print('        "Sleep_Time": 5')
    print('    }')
    print('3rd. set the environment variable CLOUDFLARE_CONFIG to the path of your config file.')
    print('4th. run the script.')
    print('    python3 cloudflare-ddns-v4.py')
    print('if you don\'t know how to get your api key, please refer to {} part 4, step 6'.format(DOC_URL))
    exit(0)

if __name__ == '__main__':
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
            HEADERS['X-Auth-Email'] = cfg['Email']
            HEADERS['X-Auth-Key'] = cfg['API_Key']
            DOMAIN_INFO = cfg['Domain_Info']
            SLEEP_TIME = cfg['Sleep_Time']
    except FileNotFoundError as e:
        print('config file not found. please check your config file.')
        usage()
        exit(-1)

    while True:
        local_ip = get_local_ip()
        if local_ip is None:
            print('get local ip failed.')
            exit(-1)
        for domain in DOMAIN_INFO:
            name = domain['name']
            type = domain['type']
            zone_id = get_zone_id(name)
            if zone_id is None:
                print('get zone id failed. please check your Email, API_KEY, and domain{}.'.format(name))
                continue
            record = get_record_by_domain(zone_id, name, type)
            if record is None:
                print('get record id failed. please check your DOMAIN.')
                continue
            if local_ip == record['content']:
                print('the record\'s content is already up to date. donot need to update.')
                continue
            UPDATE_DNS_RECORD_PAYLOAD['name'] = name
            UPDATE_DNS_RECORD_PAYLOAD['type'] = type
            UPDATE_DNS_RECORD_PAYLOAD['content'] = local_ip
            UPDATE_DNS_RECORD_PAYLOAD['proxied'] = record['proxied'] and record['proxiable']
            update_dns_record(zone_id, record['id'])

        time.sleep(SLEEP_TIME * 60)
