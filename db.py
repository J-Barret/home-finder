import re
import json

def get_DB_name():
	try:
		with open("settings.json", 'r') as file:
			data = json.load(file)
			url = data['url']
			match = re.search(r'\.com/(.*?)/\?', url)  # extracting location endpoint from url string
			if match:
				#use regular expressions to replace '-' by '.' and '/' by '_' (Windows does not allow those characters)
				DB_NAME = f"{re.sub(r'[-/]', lambda x: '.' if x.group(0) == '-' else '_', match.group(1))}.db"
			return DB_NAME
	except Exception as e:
		print(f"ERROR FETCHING SETTINGS.JSON - {e}")
