# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

class Listing:
	"""Simple object describe the item listing"""

	name = None
	url = None
	price = 0


class Spider:
	"""
	Generic superclass for search result crawlers. Subclasses must
	implement find() and identify_pages()
	"""
	url = None

	def query(self, query_str):
		"""
		Primary function that downloads the search results page, looks for
		additional pagination, and converts them into Listing objects

		:param query_str: Search query keyword to use
		"""

		# make initial http call
		response = requests.get(self.url % query_str)
		if not response.ok:
			return

		# identify number of pages and begin processing
		results = []
		soup = BeautifulSoup(response.text, "html.parser")
		stack = list(self.identify_pages(soup))

		while True:
			if response.ok:
				page_results = self.parse_page(response.text)
				results.extend(page_results)
			else:
				print "Error loading URL!"

			# move to next in stack
			if not len(stack):
				break
			next_page = stack.pop(0)
			response = requests.get(next_page)

		return results

	def parse_page(self, html):
		"""
		Given the HTML string representing a single page parse it
		and then pass the data to find() to generate

		:param html: Raw HTML of the page
		"""

		soup = BeautifulSoup(html, "html.parser")
		for name, url, price in self.find(soup):
			yield self.create_listing(name, url, price)

	def create_listing(self, name, url, price):
		listing = Listing()
		listing.name = name
		listing.url = url
		listing.price = price
		return listing

	def identify_pages(self, soup):
		"""
		Abstract method expected to be implemented by subclasses.
		Given a BeautifulSoup instance, return a list of URLs for any following pages
		that still needs to be parsed.
		"""
		raise NotImplementedError

	def find(self, soup):
		"""
		Abstract method expected to be implemented by subclasses.
		Given a BeautifulSoup instance, return a list of tuples in the format:
		(product_name, product_url, product_price)
		"""
		raise NotImplementedError


class BooksSpider(Spider):
	url = "http://search.books.com.tw/exep/prod_search.php?key=%s&cat=all"

	def identify_pages(self, soup):
		for page_number in soup.select("div.cntlisearch10 div.page span.here ~ a"):
			if page_number.get("class") in ("nxt", "prv"):
				yield page_number.attr("href")

	def find(self, soup):
		for chunk in soup.select("li.item"):
			line = chunk.select("div.input_buy ~ h3 > a")[0]
			name = line.get("title").encode("utf-8")
			url = line.get("href")
			price = chunk.select("span.price b")[0].text
			yield (name, url, price)

class MomoSpider(Spider):
	url = "http://www.momoshop.com.tw/mosearch/%s.html"

	def identify_pages(self, soup):
		# not yet implemented
		return []

	def find(self, soup):
		for chunk in soup.select("div#searchResults ul#chessboard li"):
			line = chunk.select("span#goods_name a")[0]
			#sequence = line.get("class")
			name = line.text.encode('utf-8')
			url = chunk.select("> a")[0].get("href")
			price = chunk.find("span", class_="money").text
			yield (name, url, price)

class PcHomeSpider(Spider):
	url = "http://www.pchomesearch.com.tw/index.php?q=%s"

	def identify_pages(self, soup):
		for page_number in soup.select("div.search_foot_content div.page_number a"):
			yield "http://www.pchomesearch.com.tw" + page_number.get("href")

	def find(self, soup):
		for chunk in soup.select("div.list_content_table ul"):
			name = chunk.find("li", class_="list_td_item_pdname138")
			url = chunk.find("li", class_="list_td_item_name138_link")
			price = chunk.find("span", class_="list_td_item_name138_dolors")
			yield (name.text.encode('utf-8') if name else "Unknown",
				url.text if url else "Unknown",
				price.text if price else "0")

class YahooSpider(Spider):
	url = "https://tw.search.buy.yahoo.com/search/shopping/product?p=%s"

	def identify_pages(self, soup):
		for link in soup.select("div.srp_pagination li.selected ~ li > a"):
			yield "https://tw.search.buy.yahoo.com/search/shopping/" + link.get("href")

	def find(self, soup):
		for chunk in soup.select("div#srp_result_list div.item"):
			line = chunk.select("div.srp-pdtitle a")[0]
			name = line.get("title").encode("utf-8")
			url = line.get("href")
			price = chunk.select("div.srp-pdprice > em")[0].text
			yield (name, url, price)


if __name__ == "__main__":
	import argparse
	p = argparse.ArgumentParser()
	p.add_argument("-d", "--debug", action="store_true", help="For debugging purposes")
	p.add_argument("query", help="Query string to use")
	args = p.parse_args()

	if not args.query:
		p.error("No query string defined!")

	spiders = (BooksSpider(), MomoSpider(), PcHomeSpider(), YahooSpider())
	for spider in spiders:
		for result in spider.query(args.query):
			print result.name, result.price, result.url
