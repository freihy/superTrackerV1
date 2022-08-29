class print_time:
    def __init__(self, MINS) -> None:
        self.MINS = MINS
        self.count = 0
    def iterate_time(self) -> int:
        self.count-=1
        if self.count <= 0:
            self.count = self.MINS
        return self.count