import urllib.request
import re
from collections import OrderedDict
from bs4 import BeautifulSoup
from Listing import Listing

class CarouTrack:
    def __init__(self, search_query: str) -> None:
        search_query = re.sub('[ ]', '%20', search_query)
        self.url = f'https://www.carousell.com.my/search/{search_query}'
        self.hdr = {'User-Agent': 'Mozilla/5.0'}
        # self.req = urllib.request.Request(self.url,headers=self.hdr)
        # self.page = urllib.request.urlopen(self.req)
        # self.soup = BeautifulSoup(self.page)

    '''
    0: Title, 1: Price, 2: Description
    '''
    def find_items(self, url: str):
        req = urllib.request.Request(url,headers=self.hdr)
        response = urllib.request.urlopen(req)

        title_price_desc = re.findall(r'"header_1\",\"stringContent\":\"(.{1,250})\"},{\"component\":\"header_2\",\"stringContent\":\"(.{1,15})\"},{\"component\":\"paragraph\",\"stringContent\":\"([^}]*)},{\"component\":\"paragraph\",\"stringContent\":\"(.+?(?=,\"media\"))', response.read().decode())
        return title_price_desc
    
    '''
    Takes the price in format "RMX,XXX.XX" and parses it into a float of XXXX.XX
    '''
    def clean_price(self, ori_str_price: str) -> float:
        try:
            return float(re.sub('[,]', '', ori_str_price[2:]))
        except ValueError:
            # print(f'Invalid Price: {ori_str_price}')
            return 0.00
    
    '''
    Filters the result given from find_items based on the params
    Cleans price and id tags
    returns: {title, price: float, desc, id}
    '''
    def filter(self, bundle: list, max_price: float, min_price: float, keywords: list) -> list:
        filtered_list = []
        for item in bundle:
            price = self.clean_price(item[1])
            if price >= min_price and price <= max_price and all(x.lower() in item[0].lower() for x in keywords):
                # Price changed to float above
                # id is last string 
                filtered_list.append({'title': item[0], 'price': price, 'desc': item[2], 'id': (item[3].split(":")[-1])})
                if price == 0.00:
                    print(f'Listing with invalid pricing: {item[3].split(":")[-1]}')
        return filtered_list
    
    '''
    Takes two lists of [{id: 'someid'}] and combines them, removing duplicates
    '''
    def combine(self, list1, list2) -> list:
        # print(f'List1 {list1} | List2 {list2}')
        if len(list1) >= len(list2):
            p_listings_wmm = list1
            p_listings = list2
        else:
            p_listings_wmm = list2
            p_listings = list1
        for i in range(len(p_listings_wmm)):
            for j in range(len(p_listings)):
                # print(f'i: {i} | j: {j}\n')
                if p_listings_wmm[i]["id"] == p_listings[j]["id"]:
                    if i + 1 == len(p_listings_wmm):
                        break
                    else:
                        i += 1
                    j = 0
                elif p_listings_wmm[i]["id"] != p_listings[j]["id"] and j == len(p_listings)-1:
                    p_listings.append(p_listings_wmm[i])
        return p_listings_wmm

    '''
    Find and filter listings
    Hard-coded remove duplicate listing (HTML)
    Combine recent and popular findings together
    '''
    def autopilot(self, max_price: float = 999999.99, min_price: float = 0, keywords: list = None, search_popular: bool = False, search_recent: bool = True, search_builtin_minmax: bool = False) -> list:
        def scrape(url: str, max_price: float, min_price: float, keywords: list):
            listings = self.find_items(url)
            lst = self.filter(listings, max_price, min_price, keywords)
            return lst[:int(len(lst)/2)] # Remove second half of results, are repeating results as of 1/12/2021

        combined_results = []
        retries = 0
        while len(combined_results) == 0 and retries <= 1:
            if search_popular:
                # =1 is Carousell's ID for best listings
                p_listings = scrape(self.url+'?sort_by=1', max_price, min_price, keywords)
                if search_builtin_minmax:
                    p_listings_wmm = scrape(f'{self.url}?price_end={max_price}&price_start={min_price=}&sort_by=2?', max_price, min_price, keywords)
            
            if search_popular and search_builtin_minmax:
                combined_results = (self.combine(p_listings, p_listings_wmm))
            elif search_popular:
                combined_results = p_listings
            else:
                combined_results = []
                
            if search_recent:
                # =3 is Carousell's ID for recent listings
                r_listings = scrape(self.url+'?sort_by=3', max_price, min_price, keywords)
                if search_builtin_minmax:
                    r_listings_wmm = scrape(f'{self.url}?price_end={max_price}&price_start={min_price=}&sort_by=3?', max_price, min_price, keywords)

            if search_recent:
                combined_results = self.combine(combined_results, r_listings)
            if search_builtin_minmax:
                combined_results = self.combine(combined_results, r_listings_wmm)
            retries += 1

        return combined_results

        # popular_listings = []
        # while len(popular_listings) == 0: # Repeat as sometimes it fails to capture the website
        #     url_sorted_by_recent = self.url+'?sort_by=3'
        #     url_sorted_by_popularity = self.url+'?sort_by=2'
        #     recent_listings = x(url_sorted_by_recent, max_price, min_price, keywords)
        #     popular_listings = x(url_sorted_by_popularity, max_price, min_price, keywords)

            
        #     # Popular listings combined with recent listings
        #     for listing in recent_listings:
        #         if listing["id"] not in popular_listings:
        #             popular_listings.append(listing)

        #     return popular_listings
    
    '''
    Takes a result from the autopilot and beautifies it
    '''
    def beautify(self, result: list) -> str:
        ret = ""
        for listing in result:
            title_with_dashes = re.sub('[ ]', '-', listing["title"])
            link = "https://www.carousell.com.my/p/"+title_with_dashes+'-'+listing["id"]
            ret += f'Title: {listing["title"]}\nPrice: {listing["price"]}\nLink: {link}\n\n'
        return ret
    
    '''
    Takes a result from the autopilot and beautifies it with Discord pings
    '''
    def beautify_with_pings(self, result: list) -> str:
        ret = ""
        for listing in result:
            title_with_dashes = re.sub('[ ]', '-', listing["title"])
            link = "https://www.carousell.com.my/p/"+title_with_dashes+'-'+listing["id"]
            people_to_alert = ""
            for person in listing["to_alert"]:
                people_to_alert += f'{person}, '
            ret += f'Title: {listing["title"]}\nPrice: {listing["price"]}\nLink: {link}\n{people_to_alert[:-2]}\n\n'
        return ret
    
    def print_links(self, result: list) -> str:
        ret = ""
        for listing in result:
            title_with_dashes = re.sub('[ ]', '-', listing["title"])
            link = "https://www.carousell.com.my/p/"+title_with_dashes+'-'+listing["id"]
            ret += f'{link}\n'
        return ret

    def p(self):
        req = urllib.request.Request(self.url,headers=self.hdr)
        response = urllib.request.urlopen(req)
        return BeautifulSoup(response)

# c = CarouTrack("macbook air m1")
# ans = c.autopilot(3800.00, 2000.00, ["m1", "macbook"])
# print(c.beautify(ans))
