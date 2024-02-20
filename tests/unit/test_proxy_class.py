from unittest.mock import patch
from proxy_class import *
from unittest import TestCase

DEFAULT_PROXY_WEB = "https://free-proxy-list.net/"

class TestProxyClass(TestCase):

	def test_proxy_class_creation(self):
		proxy = Proxy_Scrap("test url")
		self.assertEqual(proxy.target_webpage,"test url")
		self.assertDictEqual(proxy.headers, {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
		})
		self.assertEqual(proxy.timeout,5)
		self.assertEqual(proxy.proxy_dic,{})
		self.assertIsNone(proxy.page)
		self.assertEqual(proxy.status_code,0)
	def test_pickle_dump(self):
		pass
	def test_picke_load(self):
		pass
	def test_bs4_get_nominal(self):
		proxy_page = Proxy_Scrap("https://free-proxy-list.net/")
		page = proxy_page.bs4_get()
		if(self.assertEqual(proxy_page.status_code, 200)):
			self.assertIsNotNone(page)
	def test_selenium_get(self):
		pass
	def test_bs4_find_all_tables_bs4_nominal(self):
		proxy_page = Proxy_Scrap("https://free-proxy-list.net/")
		page = proxy_page.bs4_get()
		table_str = proxy_page.bs4_find_all_tables()
		self.assertIsNotNone(table_str)
	def test_bs4_find_all_tables_bs4_abnormal(self):
		proxy_page = Proxy_Scrap("https://free-proxy-list.net/")
		with self.assertRaises(ValueError): #since self.page is None, function should raise a value error
			proxy_page.bs4_find_all_tables()
	def test_find_proxies_and_print(self):
		proxy_page = Proxy_Scrap("https://free-proxy-list.net/")
		page = proxy_page.bs4_get()
		table_str = proxy_page.bs4_find_all_tables()
		self.assertFalse(proxy_page.proxy_dic) #dictionary should be empty at this point
		with patch("builtins.print") as mocked_print:
			proxy_page.print_proxies()
			mocked_print.assert_called_once_with("self.proxy_dic is empty.")

		proxy_dic = proxy_page.find_proxies(table_str)
		self.assertTrue(proxy_dic) #dictionary should NOT be empty at this point
		with patch("builtins.print") as mocked_print:
			proxy_page.print_proxies()
			for proxy, port in proxy_dic.items():
				mocked_print.assert_any_call(f"{proxy}: {port}")



