from parsers.criteria_selector import *
from parsers.idealista import *
from gmail_API import *
import json

def contact(email):
	gmail_auth()
	gmail_send_message(email)

def read_ranges_from_json():
    with open("settings.json", 'r') as file:
		data = json.load(file)
		price_range = (data['price_range']['min'], data['price_range']['max'])
		rooms_range = (data['rooms_range']['min'], data['rooms_range']['max'])
		size_range = (data['size_range']['min'], data['size_range']['max'])
		email = data['email']
    return price_range, rooms_range, size_range, email

if __name__ == "__main__":
	price_range, rooms_range, size_range, email = read_ranges_from_json()
	# proxy_list = get_proxy_list()
	# generate_proxy_db(proxy_list)
	# proxy_ip, proxy_port = filter_proxies_db() #looks for the first functional proxy
	# idealista_call(proxy_ip=proxy_ip,proxy_port=proxy_port)
	# idealista_parser()
	evaluate_new_houses(price_range=price_range, rooms_range=rooms_range, size_range=size_range)
	contact(email)
