from proxy_db import *

minPrice, maxPrice = (0,1000)
minRooms, maxRooms = (2,5)
minSize, maxSize = (70,150)

def evaluate_new_houses():
	db = sqlite3.connect(DB_NAME)
	cursor = db.cursor()
	cursor.execute("SELECT id, idealista_id, price, rooms, squared_meters FROM houses WHERE meets_criteria IS NULL")
	all_rows = cursor.fetchall()
	print(f"There were found {len(all_rows)} NEW houses. Evaluating...")
	for row in all_rows:
		id = row[0]
		idealista_id = row[1]
		price = row[2]
		rooms = row[3]
		size = row[4]
		if(price in range(minPrice,maxPrice+1) and rooms in range(minRooms,maxRooms+1) and size in range(minSize,maxSize+1)):
			cursor.execute("UPDATE houses SET meets_criteria = ? WHERE id = ?", ("YES",id))
		else:
			cursor.execute("UPDATE houses SET meets_criteria = ? WHERE id = ?", ("NO",id))
	db.commit()
	db.close()