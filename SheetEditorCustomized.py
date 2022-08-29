import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Job import Job

class SheetEditor:
    SPREADSHEET_NAME = 'Scraper'
    def __init__(self) -> None:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open(self.SPREADSHEET_NAME).sheet1
    
    def get_jobs(self) -> list:
        i = 2
        jobs = []
        while True:
            cur_row_value = self.sheet.row_values(i)
            if cur_row_value == []:
                break
            else:
                engine = cur_row_value[0]
                search_term = cur_row_value[1]

                min_price = float(cur_row_value[2])
                max_price = float(cur_row_value[3])

                keywords = cur_row_value[4].split(",")

                job = Job(engine, search_term, min_price, max_price, keywords)

                if len(cur_row_value) >= 6:
                    stalking = cur_row_value[5].split("`,`")
                    job.set_stalking(stalking)

                jobs.append(job)
                i += 1
        return jobs
    
    def update_stalking(self, jobs_list):
        i = 2
        for job in jobs_list:
            str_to_override = ""
            for link in job.stalking:
                str_to_override += f'{link}`,`'
            str_to_override = str_to_override[:-3]

            self.sheet.update_cell(i, 6, str_to_override)
            i+=1


    

# x = SheetEditor()
# y = x.get_jobs()
# print(y)
# str(x.get_previous_round())
# x.add_new_entry("VOID", "Red", "35", "Transfer", "Test")