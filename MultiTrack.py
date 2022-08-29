from SheetEditorCustomized import SheetEditor
from MudahTrack import MudahTrack
from CarouTrack import CarouTrack
from Listing import Listing
import re

class MultiTracker:
    
    def __init__(self) -> None:
        self.jobs = None
        self.se = SheetEditor()
        self.jobs = self.se.get_jobs()
        self.new_listings_found = None

    def get_jobs(self):
        return self.jobs
    
    def print_jobs(self):
        p = "-------------------\n"
        for job in self.jobs:
            p += f'Engine: {job.engine}\nSearch: {job.search_term}\nStalking: {job.stalking}\n-------------------\n'
        return p

    '''
    Output: 
    [(search_term, [Listing, ...]), (search_term, [Listing, ...]), ...]
    '''
    def do_jobs(self) -> list:
        accepted_listings = []

        for job in self.jobs:
            if job.engine == "MudahTrack":
                m = MudahTrack()
                search_term = m.convert_to_url_suffix(job.search_term)
                link = f'https://www.mudah.my/selangor/for-sale?q={search_term}'
                # print(f'{job.min_price}, {job.max_price}, {job.keywords}')
                scraping_results = m.scrape(m.get_html(link), job.min_price, job.max_price, job.keywords)
                accepted_listings.append((job.search_term, scraping_results))

            elif job.engine == "CarouTrack":
                c = CarouTrack(job.search_term)
                res = c.autopilot(job.max_price, job.min_price, job.keywords)
                scraping_results = []
                for listing in res: 
                    title_with_dashes = re.sub('[ ]', '-', listing["title"])
                    link = "https://www.carousell.com.my/p/"+title_with_dashes+'-'+listing["id"]
                    lobject = Listing(listing["title"], listing["price"], link, listing["desc"])
                    scraping_results.append(lobject)
                accepted_listings.append((job.search_term, scraping_results))
                
        return accepted_listings
    
    def print_results(self, listings):
        g = ""
        for group in listings:
            g += f'----------{group[0]}----------\n\n'
            for listing in group[1]:
                g += f'Listing: {listing.title}\nPrice: {listing.price}\nLink: {listing.link}\n\n'
        return g
    
    def update_local_stalking_list(self, listings):
        i = 0 
        for group in listings:
            stalking_group = []
            for listing in group[1]:
                stalking_group.append(listing.link)
            self.jobs[i].set_stalking(stalking_group)
            i += 1
    
    def update_online_stalking_list(self):
        self.se.update_stalking(self.jobs)

    def update_stalking_list(self, listings):
        self.update_local_stalking_list(listings)
        self.update_online_stalking_list()

    '''
    Finds any new listings, compared to the current jobscope
    (Use before running update_stalking_list), else you'd be comparing against the new jobscope
    '''
    def find_new_listings(self, listings):
        i = 0
        groups = []
        for group in listings:
            new_listings = []
            for listing in group[1]:
                if listing.link not in self.jobs[i].stalking:
                    new_listings.append(listing)
            i += 1
            if len(new_listings) != 0:
                groups.append((group[0], new_listings))
        return groups

'''
Sample runthrough
'''
if __name__ == '__main__':
    mt = MultiTracker()
    listings_found = mt.do_jobs()

    print(f'------------------------------------------------------\nALL VIABLE LISTINGS:\n')
    print(mt.print_results(listings_found))
    print(f'------------------------------------------------------\n')

    print(f'------------------------------------------------------\nNEW LISTINGS ONLY:\n')
    new_listings_found = mt.find_new_listings(listings_found)
    mt.update_stalking_list(listings_found)
    print(mt.print_results(new_listings_found))
    print(f'------------------------------------------------------\n')

# TODO: Stalking list may be overwritten when a listing falls out of recents 
