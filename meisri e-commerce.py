import requests as rq
import bs4 as bs4
import random
import prettytable as pt

class ProductScraper:
    def __init__(self, product_name):
        self.product_name = str(product_name).replace(" ", "+")

    def amazon_url(self):
        return f"https://www.amazon.in/s?k={self.product_name}"

    def flipkart_url(self):
        return f"https://www.flipkart.com/search?q={self.product_name}"

    def product_urls(self):
        return {"amazon": self.amazon_url(), "flipkart": self.flipkart_url()}


class WebScraper:
    def __init__(self, product_scraper):
        self.custom_headers_list = [
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
        ]
        self.urls = product_scraper.product_urls()
        self.htmls = self.get_htmls()

    def make_request(self):
        stat_codes = {}
        resp = {}
        for url in self.urls:
            req = rq.get(self.urls[url], headers=random.choice(self.custom_headers_list))
            resp[url] = req.content
            stat_codes[url] = req.status_code
        response = {"status": stat_codes, "response": resp}
        return response

    def get_htmls(self):
        self.htmls = {}
        response = self.make_request()["response"]
        for pf in response:
            html = bs4.BeautifulSoup(response[pf], "html.parser")  # Changed to 'html.parser'
            self.htmls[pf] = html
        return self.htmls

    def clean_html_tags(self, obj):
        for i in range(len(obj)):
            obj[i] = obj[i].string.strip() if obj[i].string else "N/A"

    def get_names(self):
        names = {}
        for html in self.htmls:
            name = []
            if html == 'amazon':
                name = self.htmls[html].select('div.puisg-col-inner span.a-size-medium.a-color-base.a-text-normal')
                name.extend(self.htmls[html].select('div.puisg-col-inner span.a-size-base-plus.a-color-base.a-text-normal'))
                self.clean_html_tags(name)
                for i in range(len(name)):
                    if len(name[i]) > 50:
                        name[i] = name[i][:51] + "..."
                names[html] = name
            elif html == 'flipkart':
                name = self.htmls[html].find_all('div', {'class': '_4rR01T'})
                name.extend(self.htmls[html].find_all('a', {'class': 's1Q9rs'}))
                name.extend(self.htmls[html].find_all('a', {'class': 'IRpwTa'}))
                self.clean_html_tags(name)
                names[html] = name
        return names

    def get_prices(self):
        prices = {}
        for html in self.htmls:
            price = []
            if html == 'amazon':
                price = self.htmls[html].select('div.puisg-col-inner span.a-price-whole')
                self.clean_html_tags(price)
                prices[html] = ["₹" + p if p != "N/A" else "Price Not Available" for p in price]
            elif html == 'flipkart':
                price = self.htmls[html].find_all('div', {'class': '_30jeq3'})
                self.clean_html_tags(price)
                prices[html] = price
        return prices

    def get_product_info(self):
        names = self.get_names()
        prices = self.get_prices()
        return {
            "amazon": {"name": names.get("amazon", []), "price": prices.get("amazon", [])},
            "flipkart": {"name": names.get("flipkart", []), "price": prices.get("flipkart", [])}
        }


class PriceComparison:
    @staticmethod
    def status_check(web_scraper):
        req_val = web_scraper.make_request()["status"]
        for val in req_val:
            print(f"{val} scraping status: {req_val[val]}")

    @staticmethod
    def print_table(product_info, product_website):
        names = product_info[product_website]["name"]
        prices = product_info[product_website]["price"]

        if not names or not prices:
            print(f"No data available for {product_website}")
            return

        table = pt.PrettyTable()
        table.align = "l"
        table.field_names = ["S.NO", f"{product_website.capitalize()} Product Name", "Price (INR)"]

        for no, (name, price) in enumerate(zip(names, prices), start=1):
            table.add_row([no, name, price])

        print(table)


# Main Execution Block
if __name__ == "__main__":
    product_name = input("Enter Product name to search for: ").strip()
    product_scraper = ProductScraper(product_name)
    web_scraper = WebScraper(product_scraper)

    # Check scraping status
    PriceComparison.status_check(web_scraper)

    # Print product price comparison tables
    for site in ["flipkart", "amazon"]:
        PriceComparison.print_table(web_scraper.get_product_info(), site)
