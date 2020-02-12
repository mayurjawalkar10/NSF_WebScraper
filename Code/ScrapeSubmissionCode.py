import scrapy
import time
import os
import csv
from scrapy.selector import Selector
from selenium import webdriver


class SubmissionCodeScraper(scrapy.Spider):
    name = "Submission Code scraper"

    def __init__(self):
        self.max_rows = input("Enter total number of submissions to fetch. "
                              "Put * to fetch all solutions:\n ")
        self.max_rows = float('inf') if self.max_rows == "*" else int(self.max_rows)
        self.filepath = "../Output/ScrapeData/SolutionLists/"
        self.path = "../Output/ScrapeData/"
        self.time_count = 0
        self.submission_lang = str(input("Select the Language of submissions\n"
                                         "1 : Python 3\n"
                                         "2 : Python 2\n"
                                         "3 : Java 11\n"
                                         "4 : Java 8\n"))
        self.driver = webdriver.Chrome()

    def start_requests(self):
        for filename in os.listdir(self.filepath):
            if filename.endswith((("_" + self.get_lang() + "_") if self.get_lang() == "anyProgramTypeForInvoker" else "")
                                 + "_solution_list.txt"):
                with open(self.filepath+filename, encoding='utf-16') as sub_list_file:
                    reader = csv.reader(sub_list_file, delimiter='|', quotechar='"')
                    line_count = 0
                    for row in reader:
                        line_count += 1
                        if line_count == 1:
                            continue
                        if line_count == self.max_rows + 2:
                            break
                        sub_lnk = row[2]
                        problem_name = row[6].strip().split()[0].strip()
                        lang = self.get_language(row[8].strip())
                        submission_name = problem_name + "/" + lang + "/" + row[1].strip()
                        self.timed_wait(2)
                        test_case_file = row[1].strip() + "_test_cases.txt"
                        sol_filename = row[1].strip() + "_solution.txt"
                        os.makedirs(os.path.dirname(self.path+problem_name+"/"+lang+"/"+sol_filename), exist_ok=True)

                        if test_case_file not in os.listdir(self.path+problem_name+"/"+lang+"/")\
                                or sol_filename not in os.listdir(self.path+problem_name+"/"+lang+"/"):
                            yield scrapy.Request(url=sub_lnk, callback=self.parse, meta={'filename': submission_name})

    def get_lang(self):
        if self.submission_lang == '1':
            return 'python.3'
        elif self.submission_lang == '2':
            return 'python.2'
        elif self.submission_lang == '3':
            return 'java11'
        elif self.submission_lang == '4':
            return 'java8'
        else:
            return 'anyProgramTypeForInvoker'

    def timed_wait(self, sec):
        self.time_count += sec
        if self.time_count <= 300:
            time.sleep(sec)
        else:
            self.time_count = 0
            time.sleep(200)

    def get_language(self, lang):
        if lang == 'Python 3':
            return 'python.3'
        elif lang == 'Python 2':
            return 'python.2'
        elif lang == 'Java 11':
            return 'java11'
        elif lang == 'Java 8':
            return 'java8'
        else:
            return 'anyProgramTypeForInvoker'

    def parse(self, response):
        self.driver.get(response.url)
        self.timed_wait(2)
        self.driver.find_element_by_class_name("click-to-view-tests").click()
        self.timed_wait(2)
        source = self.driver.find_element_by_id("pageContent")
        self.timed_wait(2)
        sub_resp = source.get_attribute("innerHTML")

        submission_name = response.meta.get('filename')
        test_case_file = self.path + submission_name + "_test_cases.txt"
        filename = self.path + submission_name + "_solution.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        solution_dir = self.path + submission_name[:submission_name.rindex("/")]

        if filename.split("/")[-1].strip() not in os.listdir(solution_dir):
            with open(filename, 'wb') as f:
                rows = Selector(text=sub_resp).xpath('//*[@id="program-source-text"]//li').extract()
                for row in rows:
                    words = ("".join(Selector(text=row).xpath("//*[not(self::script or self::style)]/text()")
                                     .extract()).encode('utf-8'))
                    f.write(words)
                    f.write("".join(['\n']).encode('utf-8'))

        if test_case_file.split("/")[-1].strip() not in os.listdir(solution_dir):
            with open(test_case_file, 'wb') as f:
                rows = Selector(text=sub_resp).xpath('///*[@class="roundbox"]').extract()
                for row in rows:
                    lines = Selector(text=row).xpath("//*[not(self::script or self::style)]/text()").extract()
                    for eachline in lines:
                        if len(eachline.strip()) > 0:
                            words = eachline.strip().encode('utf-8')
                            f.write(words)
                        else:
                            f.write("".join(['\n']).encode('utf-8'))
