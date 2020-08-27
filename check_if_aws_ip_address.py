#!/usr/bin/env python
import requests
import ipaddress

ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']
# amazon_ips = [item['ip_prefix'] for item in ip_ranges if item["service"] == "AMAZON"]
# ec2_ips = [item['ip_prefix'] for item in ip_ranges if item["service"] == "EC2"]
#
# amazon_ips_less_ec2 = []
#
# for ip in amazon_ips:
#     if ip not in ec2_ips:
#         amazon_ips_less_ec2.append(ip)
print('Output range record example: {}'.format(ip_ranges[0]))
while True:
    print("Enter single IP or comma-delimted list of IP's to to check against AWS region ranges: ")
    lkp_ip_list = [x.strip() for x in input().split(',')]
    hits = []
    for lkp_ip in lkp_ip_list:
        for ip_range_rec in ip_ranges:
            if ipaddress.IPv4Address(lkp_ip) in ipaddress.IPv4Network(ip_range_rec['ip_prefix']):
                found = {'lkp_ip': lkp_ip, 'ip_rec': ip_range_rec}
                hits.append(found)
                print(str(found))

print('Done')