from proxy_db import *

def evaluate_new_houses(price_range, rooms_range, size_range):
	minPrice, maxPrice = price_range
	minRooms, maxRooms = rooms_range
	minSize, maxSize = size_range

	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT id, idealista_id, price, rooms, squared_meters FROM houses WHERE meets_criteria IS NULL")
	all_rows = cursor.fetchall()
	if(len(all_rows) > 0):
		print(f"There were found {len(all_rows)} NEW houses. Evaluating...")
	else:
		print("No new houses were found")
	for row in all_rows:
		id = row[0]
		idealista_id = row[1]
		price = row[2]
		rooms = row[3]
		size = row[4]
		if(price in range(minPrice,maxPrice+1) and
			rooms in range(minRooms,maxRooms+1) and
			size in range(minSize,maxSize+1)):
			cursor.execute("UPDATE houses SET meets_criteria = ? WHERE id = ?", ("YES",id))
		else:
			cursor.execute("UPDATE houses SET meets_criteria = ? WHERE id = ?", ("NO",id))
	db.commit()
	db.close()

def already_contacted():
	pass