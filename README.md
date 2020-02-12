# NSF_WebScraper
Download the data from "codeforces.com".

Execution Instructions:
1. Run ScrapeProblemList.py to get the list of problems you want to work on.

        scrapy runspider ScrapeProblemList.py --nolog
        
2. Run ScrapeDescription.py to download the descriptions of above problems.
   It internally makes use of ProblemList.txt file generated in step 1.

        scrapy runspider ScrapeDescription.py --nolog
      
3. Run ScrapeSolutionList.py to get the list of solutions for problems fetched in above step. 
   It internally makes use of ProblemList.txt file generated in step 1.
           
        scrapy runspider ScrapeSolutionList.py --nolog
        
4. Run ScrapeSubmissionCode.py to download the solutions specified in the [PROB_ID]_[LANGUAGE]_solution_list.txt 
   file generated in step 3.

        scrapy runspider ScrapeSubmissionCode.py --nolog
        
