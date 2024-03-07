from proxy_class import *
import sqlite3

DB_NAME = "app.db"
PROXIES_TABLE_CREATION = '''
    CREATE TABLE IF NOT EXISTS proxies (
        id INTEGER PRIMARY KEY,
        proxy_ip TEXT,
        proxy_port TEXT,
        test TEXT DEFAULT UNTESTED
    )
'''
PING_TIMEOUT = 2
SAMPLE_PING_WEB = "https://www.google.com"

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
	cursor.execute("DROP TABLE IF EXISTS proxies")
	cursor.execute(PROXIES_TABLE_CREATION)
	for proxy_ip, proxy_port in proxy_list.items():
		# check if there is already a record in the proxies table with the same IP and port as the current proxy being processed
		cursor.execute("SELECT id FROM proxies WHERE proxy_ip = ? AND proxy_port = ?", (proxy_ip, proxy_port))
		existing_row = cursor.fetchone()  # returns the first row of the SELECT query. If it is None, no duplicates were found
		if existing_row is None:  # if no duplicates found, insert the proxy IP and port into the 'proxies' table
			cursor.execute("INSERT INTO proxies (proxy_ip, proxy_port) VALUES (?, ?)", (proxy_ip, proxy_port))
	db.commit()
	db.close()

def filter_proxies_db():
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT id, proxy_ip, proxy_port FROM proxies WHERE test = 'UNTESTED'")
	all_rows = cursor.fetchall()
	i = 0
	if(len(all_rows) > 0):
		print(f"There were found {len(all_rows)} UNTESTED proxies. Looking for a functional proxy...")
	for row in all_rows:
		i += 1
		print(f"\rProgress: {i}/{len(all_rows)}", end="", flush=True)
		row_id = row[0]
		proxy_ip = row[1]
		proxy_port = row[2]
		ping_result = Proxy_Scrap.ping(SAMPLE_PING_WEB, proxy_ip=proxy_ip, proxy_port=proxy_port, timeout=PING_TIMEOUT)
		if ping_result is not None:
			test_result = "PASS" if ping_result == 200 else "FAIL"
		else: #if we do not have a status_code, it was a timeout, so it is also a fail
			test_result = "FAIL"
		cursor.execute("UPDATE proxies SET test = ? WHERE id = ?", (test_result, row_id))  # update DB with test result
		if(test_result == "PASS"):
			print(f"\nSUCCESS --> Proxy IP: {proxy_ip}, Proxy port: {proxy_port}")
			db.commit()
			db.close()
			return proxy_ip, proxy_port
	db.commit()
	db.close()
	# print("No functional proxies were found in the database")
	return None, None



if __name__ == "__main__":
	proxy_list = get_proxy_list()
	generate_proxy_db(proxy_list)
	proxy_ip, proxy_port = filter_proxies_db() #looks for the first functional proxy
