class Listing:
    def __init__(self, title: str, price: float, link: str, desc: str = None) -> None:
        # Must-have variables
        self.title = title
        self.price = price
        self.link = link
        
        # Optional 
        self.desc = desc