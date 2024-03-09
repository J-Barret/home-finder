import time
import random
from proxy_db import *
import requests
import re

DB_NAME = get_DB_name()
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
RETRY_DELAY = 10
COMMON_USER_AGENTS = [
	'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    # Add more user agents as needed
]

def idealista_call(_url, _cookie, proxy_ip=None, proxy_port=None):
	url = _url
	headers = {
		'authority': 'www.idealista.com',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'es-ES,es;q=0.9',
		'cache-control': 'max-age=0',
		'cookie': _cookie,
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
	}
	proxy = {'http': f'http://{proxy_ip}:{proxy_port}',
			 'https': f'http://{proxy_ip}:{proxy_port}'}
	for i in range(3):
		try:
			print("Connecting...")
			if(proxy_ip and proxy_port):
				response = requests.get(url, proxies=proxy, headers=headers, timeout=10)
			else:
				response = requests.get(url, headers=headers, timeout=10)
			print(f"Web response was: {response.status_code}")
			if response.status_code == 200:
				with open('response.html', 'w', encoding='utf-8') as file:
					file.write(response.text)
					return True
			else:
				with open('error.html', 'w', encoding='utf-8') as file:
					file.write(response.text)
		except requests.exceptions.RequestException as e:
			print("Exception occurred when fetching webpage:", e)
		time.sleep(RETRY_DELAY)
	return False

def idealista_parser():
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute(HOUSES_TABLE_CREATION)
	with open('response.html', 'r', encoding='utf-8') as file:
		soup = BeautifulSoup(file, "html.parser")
		all_houses = soup.find_all("div",class_="item-info-container")
		for house in all_houses:
			try:
				pictures_to_skip = house.find_all('picture', class_='logo-branding')
				for picture in pictures_to_skip:
					picture.decompose()  #to prevent house_id to be mistaken with agency logo (both use the same tag "href")
				house_id = house.find("a")["href"] #gets the unique house ID
				house_price = re.search(r'\d+', house.find("span", class_="item-price").get_text().replace('.', '')).group()
				house_rooms = re.search(r'\d+', house.find("span", class_="item-detail").get_text().replace('.', '')).group()
				house_size = re.search(r'\d+', house.find("span", class_="item-detail").find_next_sibling("span", class_="item-detail").get_text().replace('.', '')).group()
				if (house_id and house_price and house_rooms and house_size):
					cursor.execute("SELECT id FROM houses WHERE "
								   "idealista_id = ? AND price = ? AND rooms = ? AND squared_meters = ?",
								   (house_id,house_price,house_rooms,house_size)) #look if house was already in DB
					existing_row = cursor.fetchone()  # returns the first row of the SELECT query. If it is None, no duplicates were found
					if existing_row is None:
						cursor.execute("INSERT INTO houses (idealista_id, price, rooms, squared_meters) VALUES (?, ?, ?, ?)",
									   (house_id,house_price,house_rooms,house_size))
			except Exception as e:
				print(f"Error parsing element. Going to the next one. {e}")
	db.commit()
	db.close()

