import scrapy
import time
import os
import csv
from html2text import HTML2Text


class ProblemDescriptionScraper(scrapy.Spider):
    name = "Problem Description scraper"

    def __init__(self):
        self.path = "../Output/ScrapeData/"
        self.max_rows = input("Enter total number of Problems to fetch the description. "
                              "Put * to fetch all Problem Descriptions:\n ")
        self.max_rows = float('inf') if self.max_rows == "*" else int(self.max_rows)

    def start_requests(self):
        with open("../Output/ScrapeData/ProblemList.txt", encoding='utf-8') as prob_list_file:
            reader = csv.reader(prob_list_file, delimiter='|', quotechar='"')

            line_count = 0
            for row in reader:
                line_count += 1
                if line_count == 1:
                    continue
                if line_count == self.max_rows+1:
                    break
                descr_lnk = row[3]
                problem_name = row[1]
                time.sleep(2)
                yield scrapy.Request(url=descr_lnk, callback=self.parse, meta={'problemName': problem_name})

    def parse(self, response):
        problem_name = response.meta.get('problemName')
        description_file_path = self.path + problem_name + "/" + problem_name + "_description.txt"
        os.makedirs(os.path.dirname(description_file_path), exist_ok=True)

        desc_html = response.xpath('//*[@id="pageContent"]/div[2]/div/div').extract()[0]
        converter = HTML2Text()
        converter.ignore_links = True
        desc_text = converter.handle(desc_html)

        with open(description_file_path, 'wb') as desc_file:
            desc_file.write(desc_text.encode("utf-16"))
