# Cloudflare-ddns-v4

A script for cloudflare's ddns service.

## Notice

Currently, only IPv4 DDNS is supported, as I have not found a good way to get the router's IPv6 address using any terminals on the LAN. However, obtaining the host's IPv6 address is simple and I will likely complete it in the next release. 
 
This script can update multiple domains at once. The "Domain_Info" key is an array where you can add information for multiple domains that you want to update. However, all domains will be updated to the same IP address. 
 
Some articles teach people to use Cloudflare's API_Token to update DNS records, but I have only found the API that requires a header containing "X-Auth-Email" and "X-Auth-Key". Therefore, this script will ask for your email and API_KEY, but it will only be used to update your DNS records. Please rest assured. 
 
The cloudflare-ddns-v4 script on OpenWrt written in Bash has a defect. It uses nslookup to get the domain's current DNS record. When you open the proxy, nslookup will get the proxy's IP address instead of the host's IP address, causing the script to always update the DNS record. This is unnecessary and will cause the domain's DNS record to be updated too frequently. This script uses Cloudflare's API to get the domain's real DNS record and keeps the domain's DNS record unchanged when the host's IP address has not changed.

## Usage

+ 1st. create a json file named cloudflare-ddns-cfg.json in some place.
+ 2nd. set the config file like this:
  ~~~ json
    {
        "Email": "your_email@email.com",
        "API_Key": "your api key",
        "Domain_Info": [
            {
                "name": "your domain",
                "type": "A" # IPv4: A; IPv6: AAAA
            }
        ],
        "Sleep_Time": 5 # polling interval, time unit: minute
    }
  ~~~
+ 3rd. set the environment variable CLOUDFLARE_CONFIG to the path of your config file.
  ~~~ bash
    export CLOUDFLARE_CONFIG=/path/to/your/config/file
  ~~~
+ 4th. run the script.
  ~~~ bash
    python3 cloudflare-ddns-v4.py
    # if you want to run it in the background, you can use nohup
    nohup python3 cloudflare-ddns-v4.py 2>&1 > cloudflare-ddns-v4.log &
  ~~~
  