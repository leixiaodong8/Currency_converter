"""
This scraper retrieves data from the website to be passed to the pipelines,
where it will be processed and stored in a sqlite3 database
"""

import datetime as dt
import scrapy
from ..items import Currency


# from https://stackoverflow.com/a/312464/
def chunks(lst, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class InvestorSpider(scrapy.Spider):
    name = 'investor'
    allowed_domains = ['br.investing.com']
    start_urls = ['https://br.investing.com/currencies/exchange-rates-table']


    def parse(self, response):
        """Parses information from website and stores it in a dictionary format"""
        # initializing instance of items class
        item = Currency()
        # scraping data and transforming it into a list
        currency_table = response.css("#exchange_rates_1 > tbody > tr > td::text").extract()
        item_list = []
        for data in currency_table:
            items = data.strip("\t").strip("\n").strip("\t") # removing nonsense
            if items.startswith("\xa0"): # country flag code
                continue
            elif items != "":
                item_list.append(items)
        # transforming the list in a dictionary
        # adapted from https://stackoverflow.com/a/63529375/13825145
        currency_list = [
            "brazilian_real",
            "american_dollar",
            "european_euro",
            "british_pound",
            "japanese_yen",
            "swiss_frank",
            "canadian_dollar",
            "australian_dollar"
            ]
        for currency_data in chunks(item_list, 8):
            for name, value in zip(currency_list, currency_data):
                # python doesn't like a comma used as a decimal point
                item[name] = float(value.replace(",", "."))
                # if the value is 1.0, that means that it is reffering to self
                if item[name] == 1.0:
                    item["name"] = name
                item["date"] = dt.datetime.now()
            yield item
