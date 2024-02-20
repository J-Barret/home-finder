from proxy_class import *
import sqlite3

DEFAULT_PROXY_WEB = "https://free-proxy-list.net/"
DB_NAME = "proxy.db"
PROXIES_TABLE_CREATION = '''
    CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY,
        proxy_ip TEXT,
        proxy_port TEXT,
        test TEXT DEFAULT UNTESTED
    )
'''
PING_TIMEOUT = 5
SAMPLE_PING_WEB = "http://www.google.es"
HTTP_PORT_TYPES = ["80", "8080", "8000", "8081", "8088", "8009", "8443"]
HTTPS_PORT_TYPES = ["443", "8443", "2087", "2096"]
MAX_LOOPS = 100

def get_proxy_list():  # no need to check for possible errors here, exceptions are managed at a lower level
	proxy_obj = Proxy_Scrap(DEFAULT_PROXY_WEB)
	proxy_obj.bs4_get()
	all_tr = proxy_obj.bs4_find_all_tables()
	proxy_list = proxy_obj.find_proxies(all_tr)
	# proxy_obj.print_proxies()

	return proxy_list


def generate_proxy_db(proxy_list):
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute(PROXIES_TABLE_CREATION)
	for proxy_ip, proxy_port in proxy_list.items():
		# check if there is already a record in the proxies table with the same IP and port as the current proxy being processed
		cursor.execute("SELECT id FROM proxies WHERE proxy_ip = ? AND proxy_port = ?", (proxy_ip, proxy_port))
		existing_row = cursor.fetchone()  # returns the first row of the SELECT query. If it is None, no duplicates were found
		if existing_row is None:  # if no duplicates found, insert the proxy IP and port into the 'proxies' table
			cursor.execute("INSERT INTO proxies (proxy_ip, proxy_port) VALUES (?, ?)", (proxy_ip, proxy_port))
	db.commit()
	db.close()

def filter_proxies_db(good_proxies_number: int):
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT id, proxy_ip, proxy_port FROM proxies WHERE test = 'UNTESTED'")
	all_rows = cursor.fetchall()
	good_proxies_found = 0
	for row in all_rows:
		row_id = row[0]
		proxy_ip = row[1]
		proxy_port = row[2]
		milis = None
		if proxy_port in HTTP_PORT_TYPES:
			ping_result = Proxy_Scrap.ping(SAMPLE_PING_WEB, proxy_ip=proxy_ip, proxy_port=proxy_port, timeout=PING_TIMEOUT)
		elif proxy_port in HTTPS_PORT_TYPES:
			ping_result = Proxy_Scrap.ping(SAMPLE_PING_WEB, proxy_ip=proxy_ip, proxy_port=proxy_port, timeout=PING_TIMEOUT)
		#if port does not appear in predefined lists, we try each one
		else:
			ping_result = Proxy_Scrap.ping(SAMPLE_PING_WEB, proxy_ip=proxy_ip, proxy_port=proxy_port, timeout=PING_TIMEOUT)
			if ping_result is None:
				ping_result = Proxy_Scrap.ping(SAMPLE_PING_WEB, proxy_ip=proxy_ip, proxy_port=proxy_port, timeout=PING_TIMEOUT)
		if ping_result is not None:
			ack, milis = ping_result
			test_result = "PASS" if ack == 200 else "FAIL"
			cursor.execute("UPDATE proxies SET test = ? WHERE id = ?", (test_result, row_id)) #update DB with test result
			if(test_result == "PASS"):
				good_proxies_found += 1
				print(f"{good_proxies_found}/{good_proxies_number} proxies found")
				if(good_proxies_found >= good_proxies_number):
					break
	db.commit()
	db.close()

if __name__ == "__main__":
	proxy_list = get_proxy_list()
	generate_proxy_db(proxy_list)
	filter_proxies_db(1) #looks for the first functional proxy