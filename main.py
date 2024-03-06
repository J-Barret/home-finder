from parsers.criteria_selector import *
from gmail_API import *

def contact():
	gmail_auth()
	gmail_send_message()

if __name__ == "__main__":
	# proxy_list = get_proxy_list()
	# generate_proxy_db(proxy_list)
	# proxy_ip, proxy_port = filter_proxies_db() #looks for the first functional proxy
	# idealista_call(proxy_ip=proxy_ip,proxy_port=proxy_port)
	# idealista_parser()
	# evaluate_new_houses()
	contact()
