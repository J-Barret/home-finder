import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import re #for regular expression operations
import subprocess
import pickle #for serializing and deserializing Python objects
from typing import Optional, Union



ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
port_pattern = r'\b\d{1,5}\b'

headers_fetch = {":authority": "proxylist.geonode.com", ":method": "GET", ":path": "/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc", ":scheme": "https",
    "Accept": "application/json, text/plain, */*", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en,es-ES;q=0.9,es;q=0.8,ru;q=0.7", "Cache-Control": "no-cache",
    "Dnt": "1", "Origin": "https://geonode.com", "Pragma": "no-cache", "Referer": "https://geonode.com/",
    "Sec-Ch-Ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}



class Proxy_Scrap:
    # Constructor method to initialize the object
    def __init__(self, url):
        self.target_webpage = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', }
        self.timeout = 5
        self.proxy_dic = {}
        self.page: Optional[Union[requests.models.Response, str]] = None
        self.status_code = 0

    @classmethod
    def ping(cls, url, proxy_ip=None, proxy_port=None, timeout=3):
        if proxy_ip and proxy_port:
            #specify both HTTP and HTTPS keys, requests.get will know which one to use depending on the "url" arg provided to the function
            proxy = {'http': f'http://{proxy_ip}:{proxy_port}',
                     'https': f'http://{proxy_ip}:{proxy_port}'}
            try:
                start_time = time.time()
                response = requests.get(url, proxies=proxy, timeout=timeout)
                end_time = time.time()
                if response.status_code == 200:
                    ping_time = (end_time - start_time) * 1000
                    return response.status_code, ping_time
                else:
                    return response.status_code, 0
            except requests.exceptions.RequestException as e:
                    return None, None

    def bs4_get(self):
        try:
            self.page = requests.get(self.target_webpage, headers=self.headers, timeout=self.timeout)
            self.status_code = self.page.status_code
            self.page.raise_for_status()  # Raise an exception for non-200 status codes
            return self.page
        except requests.exceptions.RequestException as e:
            print(f"error with bs4 request: {e}")
            return None

    def bs4_find_all_tables(self):
        if(self.page is not None):
            if type(self.page) is requests.models.Response:   #case of bs4
                soup = BeautifulSoup(self.page.content, "html.parser")

            elif type(self.page) is str:   #case of selenium -> not implemented yet
                soup = BeautifulSoup(self.page, 'html.parser')

            return soup.find_all('tr')
        else:
            raise ValueError("self.page is None. Please fetch the page content correctly first.")

    def find_proxies(self, bs4_tables):
        proxy = None
        port = None
        for current_table in bs4_tables:
            all_td = current_table.find_all('td') #extracts all "table data cell" elements -> element containing proxy IP and port
            for this_td in all_td:
                cleaned_td = this_td.text.strip() #cleaning all whitespaces
                if re.search(ipv4_pattern, cleaned_td): #looking for IPV4 IP pattern
                    proxy = cleaned_td
                    all_siblings = this_td.find_next_siblings('td') #retrieve all "td" siblings in that same "tr" element
                    for sibling in all_siblings:
                        cleaned_sibling = sibling.text.strip()
                        if re.search(port_pattern, cleaned_sibling): #looking for port pattern
                            port = cleaned_sibling
                            break
                    break
            if port and proxy:
                self.proxy_dic[proxy] = port
                proxy = None
                port = None
        if self.proxy_dic:
            return self.proxy_dic
        else:
            raise ValueError("no proxies were found.")

    def print_proxies(self):
        if self.proxy_dic:
            for key, value in self.proxy_dic.items():
                print(f"{key}: {value}")
        else:
            print("self.proxy_dic is empty.")


