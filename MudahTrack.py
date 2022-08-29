import urllib.request
import re
from Listing import Listing

class MudahTrack:

    def __init__(self) -> None:
        self.html = None
        self.applicable_listings = None

    def convert_to_url_suffix(self, search_term: str) -> str:
        return re.sub(' ', '+', search_term)

    def get_html(self, url: str) -> str:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url,headers=hdr)
        response = urllib.request.urlopen(req)
        return response.read().decode()

    def scrape(self, html: str, min_price: float, max_price: float, keywords: list = []) -> list:
        content = re.findall(r'href="https://www.mudah.my/(.{1,150})" title="(.{1,350})">', html)
        accepted_listings = []
        for i in range(1, len(content), 2):
            title = re.findall(r'">(.{1,100})</a><div class="', content[i][1])[0]
            price = re.findall(r'">(.{1,13})</div></div><div class="', content[i][1])

            if len(price) == 0 or len(title) == 0:
                print(f'Error: Title and price could not be found for {content[i][0]}')
            else:
                price = float(re.sub(' ', '', price[0])[2:])
                # print(f'Title: {title}\nPrice: {price}\n\n')
                if price >= min_price and price <= max_price and all(x.lower() in title.lower() for x in keywords):
                    listing = Listing(title, price, f'https://www.mudah.my/{content[i][0]}')
                    accepted_listings.append(listing)
                    # print(f'Title: {listing.title} | Price: {listing.price}\n')
        
        return accepted_listings

# m = MudahTrack()
# html = m.get_html("https://www.mudah.my/penang/for-sale?q=iPhone+13")
# m.scrape(html, 2000, 5000, ['iPhone','13'])