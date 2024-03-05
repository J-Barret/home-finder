import time
import random
from proxy_db import *
import requests
import re

MAIN_WEBPAGE = "https://www.idealista.com"
HOUSES_TABLE_CREATION = '''
    CREATE TABLE IF NOT EXISTS houses (
        id INTEGER PRIMARY KEY,
        idealista_id INTEGER,
        price INTEGER,
        rooms INTEGER,
        squared_meters INTEGER,
        meets_criteria TEXT,
        already_contacted TEXT 
    )
'''
RETRY_DELAY = 5
COMMON_USER_AGENTS = [
	'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    # Add more user agents as needed
]

def idealista_call(proxy_ip=None, proxy_port=None):
	url = "https://www.idealista.com/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/?ordenado-por=fecha-publicacion-desc"
	headers = {
		'authority': 'www.idealista.com',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'es-ES,es;q=0.9',
		'cache-control': 'max-age=0',
		'cookie': 'userUUID=bd3b9ce0-1aed-42e6-9094-3d93a50822cb; _pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1pbiJ9LCIxIjp7Im1vZGUiOiJvcHQtaW4ifSwiMiI6eyJtb2RlIjoib3B0LWluIn0sIjMiOnsibW9kZSI6Im9wdC1pbiJ9LCI0Ijp7Im1vZGUiOiJvcHQtaW4ifSwiNSI6eyJtb2RlIjoib3B0LWluIn0sIjYiOnsibW9kZSI6Im9wdC1pbiJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjpudWxsLCJfdCI6Im04a2p4ZjQ0fGxzdzR6eHM0In0%3D; _pcid=%7B%22browserId%22%3A%22lsw4zxryg5hg5tuc%22%2C%22_t%22%3A%22m8kjxfug%7Clsw4zyig%22%7D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbABwBrAFYAPAGZoAPqggB3ACwAvAJ71UIAL5A; didomi_token=eyJ1c2VyX2lkIjoiMThkY2NmNTktNDNlZi02YjA3LWEwNjUtODI4MTg2YzI0ZTYwIiwiY3JlYXRlZCI6IjIwMjQtMDItMjFUMTg6Mzc6NDIuOTUwWiIsInVwZGF0ZWQiOiIyMDI0LTAyLTIxVDE4OjM3OjUxLjc4M1oiLCJ2ZW5kb3JzIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6bGlua2VkaW4tbWFya2V0aW5nLXNvbHV0aW9ucyIsImM6bWl4cGFuZWwiLCJjOmFidGFzdHktTExrRUNDajgiLCJjOmhvdGphciIsImM6eWFuZGV4bWV0cmljcyIsImM6YmVhbWVyLUg3dHI3SGl4IiwiYzphcHBzZmx5ZXItR1VWUExwWVkiLCJjOnRlYWxpdW1jby1EVkRDZDhaUCIsImM6dGlrdG9rLUtaQVVRTFo5IiwiYzppZGVhbGlzdGEtTHp0QmVxRTMiLCJjOmlkZWFsaXN0YS1mZVJFamUyYyIsImM6Y29udGVudHNxdWFyZSIsImM6bWljcm9zb2Z0Il19LCJwdXJwb3NlcyI6eyJkaXNhYmxlZCI6WyJhbmFseXRpY3MtSHBCSnJySzciLCJnZW9sb2NhdGlvbl9kYXRhIiwiZGV2aWNlX2NoYXJhY3RlcmlzdGljcyJdfSwidmVyc2lvbiI6MiwiYWMiOiJBQUFBLkFBQUEifQ==; euconsent-v2=CP6VGIAP6VGIAAHABBENAnEgAAAAAAAAAAAAAAAAAACkoAMAARBqKQAYAAiDUQgAwABEGodABgACINQSADAAEQag.YAAAAAAAAAAA; discrentingbdmi=true; askToSaveAlertPopUp=true; contact5c86bf1a-2859-4c62-b164-a728306afbaa="{\'maxNumberContactsAllow\':10}"; cookieSearch-1="/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/:1708849722562"; send5c86bf1a-2859-4c62-b164-a728306afbaa="{}"; utag_main__prevCompleteClickName=; SESSION=1f7c8fa12ffd405e~822fb74a-f352-4fad-b2ef-175f3cbcfc16; utag_main__sn=7; utag_main__prevCompletePageName=010-idealista/home > portal > viewHome%3Bexp-1708938571176; utag_main__prevLevel2=010-idealista/home%3Bexp-1708938571176; datadome=aG6HsZMkU42RizHvMHAH~PbRKPZTOpvLPl8l~vYjGqlbwoWtRpQzt0bQUywdApEPdC5rsSDde6E2IYF8to2cSrmAMUWwbbWd4y3~MPcpxVfP8YsvPZvqMu~uB2pj~XkR; datadome=aGAkdxIJJ_orSV9zx3jkxusVNjp4tXTa9IjoCHouuHJh1ju87S9mfQFXy0R6E0ll6mzFFY7mrP_nu6cQGbB3Ry2cRPg8ve_bjQGpqnG9U6RmMtYV9SSYFvxRzKrrKfVq; SESSION=1f7c8fa12ffd405e~4c37b445-74f6-4d53-bc91-1861225ccb04; contact4c37b445-74f6-4d53-bc91-1861225ccb04="{\'maxNumberContactsAllow\':10}"; cookieSearch-1="/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/:1708937409502"',
		'referer': 'https://www.idealista.com/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/?ordenado-por=fecha-publicacion-desc',
		'sec-ch-device-memory': '8',
		'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
		'sec-ch-ua-arch': '"x86"',
		'sec-ch-ua-full-version-list': '"Chromium";v="122.0.6261.57", "Not(A:Brand";v="24.0.0.0", "Google Chrome";v="122.0.6261.57"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-model': '""',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'document',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-site': 'same-origin',
		'sec-fetch-user': '?1',
		'upgrade-insecure-requests': '1',
		'user-agent': random.choice(COMMON_USER_AGENTS),
		'Referer': 'https://www.idealista.com/',
		'User-Agent': random.choice(COMMON_USER_AGENTS),
		'Origin': 'https://www.idealista.com',
		'if-modified-since': 'Thu, 22 Feb 2024 07:15:00 GMT',
		'if-none-match': 'W/"29a0e0a58a6e1cbe7fe2d28280e121a3"',
		'content-type': 'application/json',
		'origin': 'https://www.idealista.com',
		'Accept': 'text/plain, */*; q=0.01',
		'x-requested-with': 'XMLHttpRequest'
	}
	proxy = {'http': f'http://{proxy_ip}:{proxy_port}',
			 'https': f'http://{proxy_ip}:{proxy_port}'}
	for i in range(5):
		try:
			if(proxy_ip and proxy_port):
				print("Connecting via proxy...")
				response = requests.get(url, proxies=proxy, headers=headers, timeout=10)
			else:
				response = requests.get(url, headers=headers, timeout=10)
			print(f"Web response was: {response.status_code}")
			if response.status_code == 200:
				with open('response.html', 'w', encoding='utf-8') as file:
					file.write(response.text)
				break
		except requests.exceptions.RequestException as e:
			print("Exception occurred when fetching webpage:", e)
		time.sleep(RETRY_DELAY)

def idealista_parser():
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute(HOUSES_TABLE_CREATION)
	with open('response.html', 'r', encoding='utf-8') as file:
		soup = BeautifulSoup(file, "html.parser")
		all_houses = soup.find_all("div",class_="item-info-container")
		for house in all_houses:
			pictures_to_skip = house.find_all('picture', class_='logo-branding')
			for picture in pictures_to_skip:
				picture.decompose()  #to prevent house_id to be mistaken with agency logo (both use the same tag "href")
			house_id = house.find("a")["href"] #gets the unique house ID
			house_price = re.search(r'\d+', house.find("span", class_="item-price").get_text().replace('.', '')).group()
			house_rooms = re.search(r'\d+', house.find("span", class_="item-detail").get_text().replace('.', '')).group()
			house_size = re.search(r'\d+', house.find("span", class_="item-detail").find_next_sibling("span", class_="item-detail").get_text().replace('.', '')).group()
			cursor.execute("SELECT id FROM houses WHERE "
						   "idealista_id = ? AND price = ? AND rooms = ? AND squared_meters = ?",
						   (house_id,house_price,house_rooms,house_size)) #look if house was already in DB
			existing_row = cursor.fetchone()  # returns the first row of the SELECT query. If it is None, no duplicates were found
			if existing_row is None:
				cursor.execute("INSERT INTO houses (idealista_id, price, rooms, squared_meters) VALUES (?, ?, ?, ?)",
							   (house_id,house_price,house_rooms,house_size))
	db.commit()
	db.close()
def is_new_house():
	#check if there are new houses in the DB
	pass

def contact(contactMessage : str):
	#parse text file to choose which message to send
	pass


if __name__ == "__main__":
	proxy_list = get_proxy_list()
	generate_proxy_db(proxy_list)
	proxy_ip, proxy_port = filter_proxies_db() #looks for the first functional proxy
	# idealista_call(proxy_ip="96.114.36.9",proxy_port="80")
	#idealista_parser()
