class Job:
    def __init__(self, engine: str, search_term: str, min_price: float, max_price: float, keywords: list, stalking: list = []) -> None:
        self.engine = engine
        self.search_term = search_term
        self.min_price = min_price
        self.max_price = max_price
        self.keywords = keywords
        self.stalking = stalking

    def set_stalking(self, stalking_list: list):
        self.stalking = stalking_list