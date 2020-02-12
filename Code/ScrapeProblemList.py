import scrapy
import time
import os
import csv
from scrapy.selector import Selector


class ProblemListScraper(scrapy.Spider):
    name = "problem list scraper"

    def __init__(self):
        self.prob_max = int(input("Enter total number of problems to fetch:\n "))
        self.order_by = input("Select an order of the problem list\n"
                              "1 : Ascending order of solution count\n"
                              "2 : Descending order of solution count\n"
                              "3 : Default\n")
        try:
            self.fileObj = self.open_file("../Output/ScrapeData/ProblemList.txt")
            self.csvObj = csv.writer(self.fileObj, delimiter='|', lineterminator='\n'
                                     , quotechar='"', quoting=csv.QUOTE_ALL)
            print("File opened.")
        except FileNotFoundError or FileExistsError:
            print("Exception while opening file.")

    def __del__(self):
        if self.fileObj is not None:
            self.fileObj.close()
            print("File closed")

    def open_file(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return open(filename, "w+", encoding="utf-8")

    def start_requests(self):
        urls = ["https://codeforces.com/problemset", ]

        for url in urls:
            if self.order_by == '1':
                url += '?order=BY_SOLVED_ASC'
            elif self.order_by == '2':
                url += '?order=BY_SOLVED_DESC'
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': 0})

    def parse(self, response):
        page = response.meta.get('page')
        curr_count = page * 100

        if page == 0:
            self.csvObj.writerow(['Count', 'ID', 'Name', 'Description', 'Difficulty', 'Total Solutions', 'Submissions'])

        for row in response.css('.problems tr')[1:]:
            if curr_count >= self.prob_max:
                break

            prob_row_data = self.extract_row_data(curr_count, response, row)
            self.csvObj.writerow(prob_row_data)
            curr_count += 1

        if curr_count < self.prob_max:
            next_page = response.xpath('.//*[@id="pageContent"]/div[3]/ul/li').extract()
            next_page = Selector(text=next_page[-1]).xpath('//a/@href').extract_first()

            if next_page:
                time.sleep(2)
                next_link = response.urljoin(next_page)
                yield scrapy.Request(url=next_link, meta={'page': page+1})

    def extract_row_data(self, curr_count, response, row):
        col = row.xpath("td")
        id = col[0].xpath('./a/text()').extract_first()
        id = id.strip() if id is not None else id
        name = col[1].xpath('.//a/text()').extract_first()
        name = name.strip() if name is not None else name
        descr_lnk = col[1].xpath('.//a/@href').extract_first()
        descr_lnk = response.urljoin(descr_lnk.strip()) if descr_lnk is not None else descr_lnk
        diff = col[3].xpath('./span/text()').extract_first()
        diff = diff.strip() if diff is not None else diff
        tot_sol = col[4].xpath('./a/text()').extract_first()
        tot_sol = tot_sol.strip() if tot_sol is not None else tot_sol
        sol_lnk = col[4].xpath('./a/@href').extract_first()
        sol_lnk = response.urljoin(sol_lnk.strip()) if sol_lnk is not None else sol_lnk

        return [str(curr_count + 1), str(id), str(name), str(descr_lnk), str(diff), str(tot_sol), str(sol_lnk)]
