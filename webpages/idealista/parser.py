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
RETRY_DELAY = 10
COMMON_USER_AGENTS = [
	'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    # Add more user agents as needed
]

def idealista_call(_url, proxy_ip=None, proxy_port=None):
	url = _url
	headers = {
		'authority': 'www.idealista.com',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'es-ES,es;q=0.9',
		'cache-control': 'max-age=0',
		'cookie': '_pprv=eyJjb25zZW50Ijp7IjAiOnsibW9kZSI6Im9wdC1pbiJ9LCIxIjp7Im1vZGUiOiJvcHQtaW4ifSwiMiI6eyJtb2RlIjoib3B0LWluIn0sIjMiOnsibW9kZSI6Im9wdC1pbiJ9LCI0Ijp7Im1vZGUiOiJvcHQtaW4ifSwiNSI6eyJtb2RlIjoib3B0LWluIn0sIjYiOnsibW9kZSI6Im9wdC1pbiJ9LCI3Ijp7Im1vZGUiOiJvcHQtaW4ifX0sInB1cnBvc2VzIjpudWxsLCJfdCI6Im04a2p4ZjQ0fGxzdzR6eHM0In0%3D; _pcid=%7B%22browserId%22%3A%22lsw4zxryg5hg5tuc%22%2C%22_t%22%3A%22m8kjxfug%7Clsw4zyig%22%7D; _pctx=%7Bu%7DN4IgrgzgpgThIC4B2YA2qA05owMoBcBDfSREQpAeyRCwgEt8oBJAE0RXSwH18yBbABwBrAFYAPAGZoAPqggB3ACwAvAJ71UIAL5A; didomi_token=eyJ1c2VyX2lkIjoiMThkY2NmNTktNDNlZi02YjA3LWEwNjUtODI4MTg2YzI0ZTYwIiwiY3JlYXRlZCI6IjIwMjQtMDItMjFUMTg6Mzc6NDIuOTUwWiIsInVwZGF0ZWQiOiIyMDI0LTAyLTIxVDE4OjM3OjUxLjc4M1oiLCJ2ZW5kb3JzIjp7ImRpc2FibGVkIjpbImdvb2dsZSIsImM6bGlua2VkaW4tbWFya2V0aW5nLXNvbHV0aW9ucyIsImM6bWl4cGFuZWwiLCJjOmFidGFzdHktTExrRUNDajgiLCJjOmhvdGphciIsImM6eWFuZGV4bWV0cmljcyIsImM6YmVhbWVyLUg3dHI3SGl4IiwiYzphcHBzZmx5ZXItR1VWUExwWVkiLCJjOnRlYWxpdW1jby1EVkRDZDhaUCIsImM6dGlrdG9rLUtaQVVRTFo5IiwiYzppZGVhbGlzdGEtTHp0QmVxRTMiLCJjOmlkZWFsaXN0YS1mZVJFamUyYyIsImM6Y29udGVudHNxdWFyZSIsImM6bWljcm9zb2Z0Il19LCJwdXJwb3NlcyI6eyJkaXNhYmxlZCI6WyJhbmFseXRpY3MtSHBCSnJySzciLCJnZW9sb2NhdGlvbl9kYXRhIiwiZGV2aWNlX2NoYXJhY3RlcmlzdGljcyJdfSwidmVyc2lvbiI6MiwiYWMiOiJBQUFBLkFBQUEifQ==; euconsent-v2=CP6VGIAP6VGIAAHABBENAnEgAAAAAAAAAAAAAAAAAACkoAMAARBqKQAYAAiDUQgAwABEGodABgACINQSADAAEQag.YAAAAAAAAAAA; discrentingbdmi=true; askToSaveAlertPopUp=true; userUUID=5d8917e3-c18a-49d5-83a5-9c18d9714485; galleryHasBeenBoosted=true; SESSION=44da8a4033895600~5a76d67f-6014-4df6-a0c0-be148545eaee; utag_main__sn=15; utag_main_ses_id=1709805686049%3Bexp-session; utag_main__ss=0%3Bexp-session; utag_main__prevVtUrl=https://www.idealista.com/%3Bexp-1709810038544; utag_main__prevVtUrlReferrer=%3Bexp-1709810038544; utag_main__prevVtSource=Direct traffic%3Bexp-1709810038544; utag_main__prevVtCampaignName=organicWeb%3Bexp-1709810038544; utag_main__prevVtCampaignCode=%3Bexp-1709810038544; utag_main__prevVtCampaignLinkName=%3Bexp-1709810038544; utag_main__prevVtRecipientId=%3Bexp-1709810038544; utag_main__prevVtProvider=%3Bexp-1709810038544; contact5a76d67f-6014-4df6-a0c0-be148545eaee="{\'maxNumberContactsAllow\':10}"; utag_main__prevCompleteClickName=; cookieSearch-1="/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/:1709808152267"; send5a76d67f-6014-4df6-a0c0-be148545eaee="{}"; utag_main__pn=12%3Bexp-session; utag_main__se=21%3Bexp-session; utag_main__st=1709810880109%3Bexp-session; utag_main__prevCompletePageName=010-idealista/home > portal > viewLastSearchModule%3Bexp-1709812680116; utag_main__prevLevel2=010-idealista/home%3Bexp-1709812680116; datadome=T~4L_tLECKGkilCqU4lC8U7a_sQyDT6OgsClMtKLrCerpWdtxeVs8jKV_Sv4fKUdkjvOODaZRIRaiF3RwG~_46m2YPmFYTocxdv4_OCyTXU42un~TsgEgW8F8Ab5en7P; datadome=aGAkdxIJJ_orSV9zx3jkxusVNjp4tXTa9IjoCHouuHJh1ju87S9mfQFXy0R6E0ll6mzFFY7mrP_nu6cQGbB3Ry2cRPg8ve_bjQGpqnG9U6RmMtYV9SSYFvxRzKrrKfVq; cookieSearch-1="/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/:1708937409502"',
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

