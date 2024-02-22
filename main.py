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
def idealista_call(proxy_ip=None, proxy_port=None):
	url = "https://www.idealista.com/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/?ordenado-por=fecha-publicacion-desc"
	headers = {
		'authority': 'www.idealista.com',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'es-ES,es;q=0.9',
		'cache-control': 'max-age=0',
		'referer': 'https://www.idealista.com/',
		'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
		'Referer': 'https://www.idealista.com/',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
		'Origin': 'https://www.idealista.com',
		'Accept': 'text/plain, */*; q=0.01',
		'X-Requested-With': 'XMLHttpRequest',
		'content-type': 'application/json',
		'origin': 'https://www.idealista.com',
		'Cookie': 'datadome=xURHdXG~Ji2nHBmzpWAiJ2J141xvgwmbrItkbLW5djwr09rAKiG~buy66kWChdA0ofbyWRuOOESbzVnJaVuQyjSjohBWMm8Q6PE5SjlJY8q8vALk7UzSO37~bIs1gGvH; SESSION=1f7c8fa12ffd405e~34caa701-3ced-4ece-a60e-b72d0dd7443d; contact34caa701-3ced-4ece-a60e-b72d0dd7443d="{\'maxNumberContactsAllow\':10}"; cookieSearch-1="/alquiler-viviendas/san-cristobal-de-la-laguna/la-laguna/:1708543555018"; userUUID=8b3fad0a-00f7-4e87-9688-cb6c3efbe4bd'
	}
	proxy = {'http': f'http://{proxy_ip}:{proxy_port}',
			 'https': f'http://{proxy_ip}:{proxy_port}'}
	try:
		if(proxy_ip and proxy_port):
			response = requests.get(url, proxies=proxy, headers=headers)
		else:
			response = requests.get(url, headers=headers)
		print(f"Web response was: {response.status_code}")
		with open('response.html', 'w', encoding='utf-8') as file:
			file.write(response.text)
	except requests.exceptions.RequestException as e:
		print("Exception occurred when fetching Idealista:", e)

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
	idealista_call()
	idealista_parser()
