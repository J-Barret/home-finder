import requests
from bs4 import BeautifulSoup
import re #for regular expression operations
from typing import Optional, Union


DEFAULT_PROXY_WEB = "https://free-proxy-list.net/"
ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
port_pattern = r'\b\d{1,5}\b'
num_retries = 1

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
    def ping(cls, url, proxy_ip=None, proxy_port=None, timeout=5):
        if proxy_ip and proxy_port:
            #specify both HTTP and HTTPS keys, requests.get will know which one to use depending on the "url" arg provided to the function
            proxy = {'http': f'http://{proxy_ip}:{proxy_port}',
                     'https': f'http://{proxy_ip}:{proxy_port}'}
            for attempt in range(num_retries):
                try:
                    response = requests.get(url, proxies=proxy, timeout=timeout)
                    #print(response.status_code)
                    return response.status_code
                except requests.exceptions.RequestException as e:
                    if(attempt < num_retries-1):
                        continue
                    else:
                        #print("Exception occurred:", e)
                        return None

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
            #Only looking for HTTPS proxies
            if current_table.find("td", class_="hx") and current_table.find("td", class_="hx").text == "yes":
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


