import scrapy
import time
import os
import csv
from scrapy.selector import Selector
from selenium import webdriver


class SolutionListScraper(scrapy.Spider):
    name = "solution list scraper"

    def __init__(self):
        self.submission_max = input("Enter total number of submissions to fetch. Put * to fetch all submissions:\n ")
        self.submission_max = float('inf') if self.submission_max == "*" else int(self.submission_max)

        self.submission_lang = str(input("Select the Language of submissions\n"
                                         "1 : Python 3\n"
                                         "2 : Python 2\n"
                                         "3 : Java 11\n"
                                         "4 : Java 8\n"))

        self.verdict = str(input("Select the verdict of the submission\n"
                                 "1 : OK\n"
                                 "2 : Rejected\n"
                                 "3 : Default / Any Verdict\n"))

        self.driver = webdriver.Chrome()
        self.path = "../Output/ScrapeData/"

    def __del__(self):
        self.driver.close()

    def get_verdict(self):
        if self.verdict == '1':
            return 'OK'
        elif self.verdict == '2':
            return 'REJECTED'
        else:
            return 'anyVerdict'

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

    def start_requests(self):
        with open("../Output/ScrapeData/ProblemList.txt", encoding='utf-8') as prob_list_file:
            reader = csv.reader(prob_list_file, delimiter='|',  quotechar='"')

            line_count = 0
            for row in reader:
                line_count += 1
                if line_count == 1:
                    continue
                sol_lnk = row[6]
                problem_name = row[1]
                yield scrapy.Request(url=sol_lnk, callback=self.parse, meta={'problemName': problem_name})

    def get_response_by_lang_and_verdict(self, response, page):
        self.driver.get(response.url)
        time.sleep(2)
        if page == 0:
            self.driver.find_element_by_xpath("//select[@name='programTypeForInvoker']/option[@value='"
                                              + self.get_lang() + "']").click()
            time.sleep(2)
            self.driver.find_element_by_xpath("//select[@name='verdictName']/option[@value='"
                                              + self.get_verdict() + "']").click()
            time.sleep(2)
            self.driver.find_element_by_xpath("//input[@value='Apply']").submit()
            time.sleep(2)
        resp = self.driver.find_element_by_class_name("status-frame-datatable")
        return resp.get_attribute('innerHTML')

    def parse(self, response):
        page = response.meta.get('page')
        page = 0 if page is None else page
        open_mode = 'w+' if page == 0 else 'a'
        cur_sub_cnt = page * 50

        req_response = self.get_response_by_lang_and_verdict(response, page)
        time.sleep(2)

        problem_name = response.meta.get('problemName')
        solution_list_file_path = self.path + "SolutionLists" + "/" \
                                            + problem_name + "_" + self.get_lang() + "_solution_list.txt"

        os.makedirs(os.path.dirname(solution_list_file_path), exist_ok=True)

        with open(solution_list_file_path, open_mode, encoding="utf-16") as problem_file:
            problem_file = csv.writer(problem_file, delimiter='|', lineterminator='\n'
                                      , quotechar='"', quoting=csv.QUOTE_ALL)
            if page == 0:
                problem_file.writerow(['Count', 'Submission ID', 'Submission Link', 'Submission Date',
                                       'Author', 'Author Link', 'Problem Name', 'Problem Link',
                                       'Solution Language', 'Verdict', 'Time Taken', 'Memory Required'])

            for submissions_row in Selector(text=req_response).css('tr')[1:]:
                if cur_sub_cnt >= self.submission_max:
                    break

                sub_colm = submissions_row.xpath("td")
                if len(sub_colm) < 2:
                    break
                id = sub_colm[0].xpath('./a/text()').extract_first()
                submission_link = sub_colm[0].xpath('./a/@href').extract_first()
                submission_date = sub_colm[1].xpath('./text()').extract_first()
                author = sub_colm[2].xpath('./a/text()').extract_first()
                author_link = sub_colm[2].xpath('./a/@href').extract_first()
                prob = sub_colm[3].xpath('./a/text()').extract_first()
                prob_link = sub_colm[3].xpath('./a/@href').extract_first()
                lang = sub_colm[4].xpath('./text()').extract_first()
                verdict = sub_colm[5].xpath('./span/span/text()').extract_first()
                time_taken = sub_colm[6].xpath('./text()').extract_first()
                memory_req = sub_colm[7].xpath('./text()').extract_first()

                if id is not None:
                    id = id.strip()
                if submission_link is not None:
                    sub_link = "https://codeforces.com" + submission_link.strip()
                if submission_date is not None:
                    submission_date = submission_date.strip()
                if author is not None:
                    author = author.strip()
                if author_link is not None:
                    author_link = "https://codeforces.com" + author_link.strip()
                if prob is not None:
                    prob = prob.strip()
                if prob_link is not None:
                    prob_link = "https://codeforces.com" + prob_link.strip()
                if lang is not None:
                    lang = lang.strip()
                if verdict is not None:
                    verdict = verdict.strip()
                if time_taken is not None:
                    time_taken = time_taken.strip()
                if memory_req is not None:
                    memory_req = memory_req.strip()

                row = [str(cur_sub_cnt + 1), str(id), str(sub_link), str(submission_date),
                       str(author), str(author_link), str(prob), str(prob_link),
                       str(lang), str(verdict), str(time_taken), str(memory_req)]

                problem_file.writerow(row)

                cur_sub_cnt += 1

            if cur_sub_cnt < self.submission_max:
                nxt_resp = self.driver.find_element_by_id("pageContent")
                nxt_req_response = nxt_resp.get_attribute('innerHTML')
                next_page = Selector(text=nxt_req_response).xpath('//div[8]/div/ul/li').extract()

                if len(next_page) == 0:
                    return

                next_page = Selector(text=next_page[-1]).xpath('//a/@href').extract_first()

                if next_page:
                    next_link = response.urljoin(next_page)
                    yield scrapy.Request(url=next_link, meta={'problemName': problem_name, 'page': page + 1},
                                         callback=self.parse)
