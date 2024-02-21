from proxy_db import *

MAIN_WEBPAGE = "https://www.idealista.com"

if __name__ == "__main__":
	proxy_list = get_proxy_list()
	generate_proxy_db(proxy_list)
	filter_proxies_db() #looks for the first functional proxy
	#START BACKEND IDEALISTA CALLING AND FILTERING