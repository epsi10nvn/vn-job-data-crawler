import scrapy
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.chrome.options import Options 
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.common.proxy import Proxy, ProxyType
import random
from seleniumbase import Driver
import json
from scrapy.exceptions import CloseSpider
import requests

class LinkedinSpider(scrapy.Spider):
    name = "linkedin"
    # api_key_old = "67421f044f9936f02c85c60c"
    api_key = "67421f044f9936f02c85c60c"
    allowed_domains = ["api.scrapingdog.com"]
    start_urls = [f"http://api.scrapingdog.com/linkedinjobs?page=1&geoid=104195383&field=data&api_key={api_key}"]
    
    page = 1
    url = None
    # http://api.scrapingdog.com/linkedinjobs?page=1&geoid=104195383&field=data&api_key=6741ac835ac1f2ad0a815c04

    def parse(self, response):
        if self.page == 2:
            raise CloseSpider('Limited request from api.scrapingdog...')

        resp = json.loads(response.body)
        for job in resp:
            job_id = job.get('job_id')
            url_job = f"http://api.scrapingdog.com/linkedinjobs?job_id={job_id}&api_key={self.api_key}"

            job_posting_date = job.get('job_posting_date')

            yield SeleniumRequest(
                url=url_job,
                callback=self.parse_job_details,
                meta={'job_posting_date': job_posting_date, 'job_id': job_id}
            )
            print('-------------------------')
        self.page += 1

        self.url=f"http://api.scrapingdog.com/linkedinjobs?page={self.page}&geoid=104195383&field=data&api_key={self.api_key}"

        yield SeleniumRequest(
            url=self.url,
            wait_time=20,
            callback=self.parse
        )

    def parse_job_details(self, response):
        job_posting_date = response.meta['job_posting_date']
        job_id = response.meta['job_id']

        resp = json.loads(response.body)[0]

        # Yield or store the job details
        yield {
            'job_id': job_id,
            'job_position': resp.get('job_position'),
            'jobs_status': resp.get('jobs_status'),
            'job_location': resp.get('job_location'),
            'company_name': resp.get('company_name'),
            'job_posting_time': resp.get('job_posting_time'),
            'base_pay': resp.get('base_pay'),
            'job_description': resp.get('job_description'),
            'Seniority_level': resp.get('Seniority_level'),
            'Employment_type': resp.get('Employment_type'),
            'Job_function': resp.get('Job_function'),
            'Industries': resp.get('Industries'),
            'job_posting_date': job_posting_date
        }

# https://api.scrapingdog.com/