#!/usr/bin/python3

class color:
    yellow = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end  = '\033[0m'

import sys
import re
import requests
import json
import argparse, textwrap
import configparser
from bs4 import BeautifulSoup

""" Setup Argument Parameters """
parser = argparse.ArgumentParser(description='[INFO] Example: python3 USStaffMana.py -c telsa -e telsa.com -n 0', formatter_class=argparse.RawTextHelpFormatter)
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-c', '--company', help='Company Name', required=True)
requiredNamed.add_argument('-e', '--email', help='Company Email Domain', required=True)
requiredNamed.add_argument('-n', '--naming', help= textwrap.dedent('''\
    User Name Format: 
    \t[0] Auto (Hunter.io) 
    \t[1] FirstLast
    \t[2] FirstMiddleLast
    \t[3] FLast
    \t[4] FirstL
    \t[5] First.Last
    \t[6] Last.First'''), required=True)
args = parser.parse_args()

""" API-KEY """
config = configparser.RawConfigParser()
config.read("USStaffMama.cfg")
api_key = config.get('API_KEYS', 'hunter_api')

def error():
    print("[ERROR] Something went wrong!")
    sys.exit()

def banner():
    print
    print("   __  ____________ __        __________  ___                       ")
    print("  / / / / ___/ ___// /_____ _/ __/ __/  |/  /___ _____ ___  ____ _  ")
    print(" / / / /\__ \\\\__ \/ __/ __ `/ /_/ /_/ /|_/ / __ `/ __ `__ \/ __ `/  ")
    print("/ /_/ /___/ /__/ / /_/ /_/ / __/ __/ /  / / /_/ / / / / / / /_/ /   ")
    print("\____//____/____/\__/\__,_/_/ /_/ /_/  /_/\__,_/_/ /_/ /_/\__,_/    ")
    print("                                                 [bigb0ss]          ")
    print                                                                  
    print

def escape_csv(value):
    return value
    return value.replace('"', '\\"').replace(',', '\\,')

# US Staff Search
def search(company, email, prefix):
    csv = []

    url = "https://bearsofficialsstore.com/company/%s/page1" % company
    
    r = requests.get(url)

    if r.status_code != 200:
        print("[ERROR] 404 Error! The company name needs to be verified. Go to https://bearsofficialsstore.com/ and find the EXACT company name (e.g., t-mobile != t_mobile)")
        sys.exit()
    
    content = (r.text)
    contentSoup = BeautifulSoup(content, 'html.parser')

    # Finding the last page
    for i in contentSoup.find_all('a'):
        page = i.get('href')
    match = re.search('page([0-9]*)', page)

    if match == None:
        lastPage = 1
        lastPageNum = 2
        print("[INFO] Total Pages: %s" % lastPage) 
    else:
        lastPage = match.group()[4:]
        lastPage = int(lastPage)
        lastPageNum = lastPage + 1 # you know what python does for numbering
        print("[INFO] Total Pages: %s" % lastPage) 

    for page in range(1, lastPageNum):
               
        url = "https://bearsofficialsstore.com/company/%s/page%s" % (company, page)
        print("[INFO] Fetching usernames: %s" % url)
        
        r = requests.get(url)
        content = (r.text)
        contentSoup = BeautifulSoup(content, 'html.parser')
        user_divs = contentSoup.find_all(lambda tag: tag.has_attr('class') and ' '.join(tag['class']) in ['empl row pt-2 pb-2 mb-2 bg-light', 'empl row pt-2 pb-2 mb-2'])   
        for div in user_divs:    
            name_tag = div.find('strong', class_='name')
            name = escape_csv(name_tag.text) if name_tag else 'N/A'

            city_tag = div.find('span', class_='d-block')
            city = escape_csv(city_tag.text) if city_tag else 'N/A'

            years_tag = div.find('div', class_='col-lg-2 col-md-2 cur_p')
            years = escape_csv(years_tag.text) if years_tag else 'N/A'

            job_tag = div.find('div', class_='col-lg-4 col-md-3 cur_p')
            job = escape_csv(job_tag.text) if job_tag else 'N/A'

            industry_tag = div.find('div', class_='col-lg-2 col-md-2 cur_p')
            industry = escape_csv(industry_tag.text) if industry_tag else 'N/A'


            print(f"\"{name}\",\"{city}\",\"{years}\",\"{job}\",\"{industry}\"")
              
            # CSV
            csv.append('"%s","%s","%s","%s","%s"' % (name, city, years, job, industry))
            f = open('{}.csv'.format(company), 'w')
            f.writelines('\n'.join(csv))
            f.close()

if __name__ == '__main__':
    banner()

    company = args.company
    company = company.lower()
    
    email = args.email
    email = email.lower()
    if "." not in email:
        print(color.red + "[ERROR] Incorrect Email Format." + color.end)
        sys.exit()

    prefix = args.naming
    prefix = prefix.lower()

    if prefix == "0":
        # Hunter.io
        print("[INFO] Hunter.io search...")
        url_hunter = "https://api.hunter.io/v2/domain-search?domain=%s&api_key=%s" % (email, api_key)
        r = requests.get(url_hunter)

        if r.status_code != 200:
            print("[ERROR] Something is wrong accessing Hunter.io")
            sys.exit()

        content = json.loads(r.text)
        prefix = content['data']['pattern']
        print("[INFO] %s" % prefix)
        if prefix:
            prefix = prefix.replace("{","").replace("}", "")
            if prefix == "firstlast" or prefix == "firstmlast" or prefix == "flast" or prefix == "firstl" or prefix =="first" or prefix == "first.last" or prefix == "fmlast" or prefix == "lastfirst":
                print("[INFO] Found %s Naming Scheme" % prefix)
            else:
                print(color.red + "[ERROR] Auto-search Failed. Select the user name format from the option." + color.end)
                sys.exit()
        else:
            print(color.red + "[ERROR] Auto-search Failed. Select the user name format from the option." + color.end)
            sys.exit()

    # Scraping
    search(company, email, prefix)

    print("[INFO] US Staff Scrapping Done!")
