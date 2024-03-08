from gmail_API import *
from webpages.idealista.criteria_selector import *
from webpages.idealista.parser import *
import json
import keyboard
import time

PROXY_RETRY_TIME = 60
WEBPAGE_RETRY_TIME = 120

def contact(email, new_houses_urls):
	gmail_auth()
	gmail_send_message(email, new_houses_urls)

def read_ranges_from_json():
	with open("settings.json", 'r') as file:
		data = json.load(file)
		price_range = (data['price_range']['min'], data['price_range']['max'])
		rooms_range = (data['rooms_range']['min'], data['rooms_range']['max'])
		size_range = (data['size_range']['min'], data['size_range']['max'])
		email = data['email']
		proxy_protection = data['proxy_protection']
		url = data['url']
		return price_range, rooms_range, size_range, email, proxy_protection, url

def function_with_proxy(price_range, rooms_range, size_range, email, url):
	proxy_list = get_proxy_list()
	generate_proxy_db(proxy_list)
	print("RUNNING WITH PROXY... Press 'q' if you want to exit the program")
	#-------------------------MAIN LOOP --------------------------------------------
	while True:
		proxy_ip, proxy_port = filter_proxies_db() #looks for the first functional proxy
		if(proxy_ip is not None and proxy_port is not None):
			if (idealista_call(_url=url, proxy_ip=proxy_ip,proxy_port=proxy_port) is True):
				idealista_parser()
				evaluate_new_houses(price_range=price_range, rooms_range=rooms_range, size_range=size_range)
				new_houses_urls = get_new_urls()
				if new_houses_urls:
					contact(email, new_houses_urls)
					print("Mail sent!")
				print(f"Going to sleep, checking webpage again in {WEBPAGE_RETRY_TIME} seconds")
				time.sleep(WEBPAGE_RETRY_TIME)
			#if a connection was not established, look for the next UNTESTED proxy in the following loop
		else:
			print(f"\nNo functional proxies were found. Scraping new proxies in {PROXY_RETRY_TIME} seconds")
			time.sleep(PROXY_RETRY_TIME)
			proxy_list = get_proxy_list()
			generate_proxy_db(proxy_list)
		if keyboard.is_pressed('q'):
			break

def function_without_proxy(price_range, rooms_range, size_range, email, url):
	print("RUNNING WITHOUT PROXY... Press 'q' if you want to exit the program")
	#-------------------------MAIN LOOP --------------------------------------------
	while True:
		if (idealista_call(_url=url) is True):
			idealista_parser()
			evaluate_new_houses(price_range=price_range, rooms_range=rooms_range, size_range=size_range)
			new_houses_urls = get_new_urls()
			if new_houses_urls:
				contact(email, new_houses_urls)
				print("Mail sent!")
		print(f"Going to sleep, checking webpage again in {WEBPAGE_RETRY_TIME} seconds")
		time.sleep(WEBPAGE_RETRY_TIME)
		if keyboard.is_pressed('q'):
			break

def main():
	price_range, rooms_range, size_range, email, proxy_protection, url = read_ranges_from_json()
	if(proxy_protection == "yes"):
		function_with_proxy(price_range, rooms_range, size_range, email, url)
	elif(proxy_protection == "no"):
		function_without_proxy(price_range, rooms_range, size_range, email, url)
	else:
		print("Set a valid proxy_protection value in 'settings.json' please")

if __name__ == "__main__":
	main()

