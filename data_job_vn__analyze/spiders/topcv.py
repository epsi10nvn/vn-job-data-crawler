from typing import Iterable
import time
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


min_wait = 1
max_wait = 5

class JobDetailsInformation():
    def __init__(self):
        self.inside_title = None
        self.salary = "Nagotiation"
        self.position = None
        self.by_expiration_date = None
        self.views = 0
        self.city = None
        self.deadline_submit = None

        self.description = None
        self.requirements = None
        self.work_time = None

        self.posted_date = None
        self.level = None
        self.field = None
        self.skills = None
        self.main_industry = list()
        self.cv_language = None
        self.yoe = None
        self.num_of_recruit = None
        self.work_form = None
        self.gender_require = None

        self.relation_fields = list()
        self.work_address = None
        self.company_size = None
        self.major_field = None
        self.key_words = list()
        self.area = list()

class TopcvSpider(scrapy.Spider):
    name = "topcv"
    allowed_domains = ["www.topcv.vn"]
    start_urls = ["https://www.topcv.vn/"]
    key_word = 'data engineer'

    def start_requests(self):
        url = self.start_urls[0]
        yield SeleniumRequest(url=url, wait_time=5, callback=self.parse, screenshot=True)
    
    def parse(self, response):
        driver = Driver(uc=True, headed=False)
        driver.set_window_size(1920, 1080)

        try:
            driver.uc_open_with_reconnect("https://www.topcv.vn/viec-lam-it", reconnect_time=6)
            time.sleep(5)
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@id="keyword"]'))
            )
            for c in self.key_word:
                search_box.send_keys(c)
                time.sleep(random.uniform(0.2, 1))
            
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            driver.uc_gui_click_captcha()
            time.sleep(5)
            '''
            Get outside information
            '''
            # num_navs = len(driver.find_elements(By.XPATH, '//div[@class="sc-62971003-0 fkwXHN"]//ul//li'))
            num_navs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="text-center"]//ul//li//a'))
            )
            next_pages = {} 
            details_link = {}
            cur_idx = 0
            idx = 0
            # Extract href attributes
            for nav in num_navs[:-1]: 
                cur_idx += 1
                next_pages[cur_idx] = nav.get_attribute('href')
            for cur_idx in range(len(num_navs)):
                print(f"Current i: {cur_idx + 1}")
                if cur_idx > 0:
                    driver.uc_open_with_reconnect(next_pages[cur_idx], reconnect_time=6)
                    time.sleep(3)
                    cur_idx += 1

                last_height = driver.execute_script("return document.body.scrollHeight")  # Chiều cao ban đầu của trang
                while True:
                    # Cuộn xuống
                    ActionChains(driver).scroll_by_amount(0, 10000).perform()
                    time.sleep(1)  # Chờ trang tải thêm nội dung
                    
                    # Lấy chiều cao mới sau khi cuộn
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    
                    # Nếu chiều cao không đổi, thoát khỏi vòng lặp
                    if new_height == last_height:
                        # print("Không còn nội dung mới để tải.")
                        break
                    
                    last_height = new_height  # Cập nhật chiều cao mới

                time.sleep(3)
                job_blocks = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.box-header'))
                )
                # time.sleep(100)
                for i, job in enumerate(job_blocks):
                    try:
                        job_title = job.find_element(By.XPATH, './/h3//a')
                        # Tìm thẻ <span> bên trong thẻ <a>
                        job_title_text = job_title.find_element(By.XPATH, './/span').text
                        company_name = job.find_element(By.XPATH, './/a[@class="company"]').text
                        update_time = job.find_element(By.XPATH, './/label[@class="deadline"]').text
                        city = job.find_element(By.XPATH, './/div[@class="label-content"]//label[@class="address"]').text
                        remain_time = job.find_element(By.XPATH, './/div[@class="label-content"]//label[@class="time"]').text
                #         try:
                #             span_element = job_title.find_element(By.TAG_NAME, 'span')
                #             span_text = span_element.text
                #             job_title_text = ' '.join(job_title_text.split()[len(span_text.split()):])
                #         except Exception:
                #             span_text = None  # Nếu không có <span> thì giá trị là None

                        details_link[idx] = {'href': job_title.get_attribute('href'), 'title': job_title_text, 'company_name': company_name, 'update_time': update_time, 'remain_time': remain_time}
                        # idx += 1
                        # yield {   
                        #         '_id': idx, 
                        #         'outside_details': 
                        #             {
                        #                 'title': job_title_text,
                        #                 'company': company,
                        #                 'update_time': update_time,
                        #                 'city': city,
                        #                 'remain_time': remain_time
                        #             } 
                        #     }
                        idx += 1
                    except Exception as e:
                        print(f'Lỗi khi lấy thông tin từ trang {cur_idx}, job {i}: {e}')
                        yield {f'Lỗi khi lấy thông tin từ trang {cur_idx}, job {i}: {e}'}
                        # 
            print(details_link)
            for idx, data in details_link.items():
                # get outside information
                url = data['href']
                company_name = data['company_name']
                update_time = data['update_time']
                remain_time = data['remain_time']
                title = data['title']


                print(f'Current {idx}: {url}')
                # if idx == 2:
                #     break
                try:
                    driver.uc_open_with_reconnect(url, reconnect_time=6)
                    time.sleep(10)
                    try:
                        try:
                            more_skills_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="box-category collapsed"]//span[@class="box-category__expand collapsed-action"]'))
                            )
                            more_skills_button.send_keys(Keys.RETURN)
                            time.sleep(3)
                        except Exception as e:
                            print('No more skills button found!')
                        '''
                        Get all details information
                        '''
                        # Salary, city and years of experiment
                        details_infor = JobDetailsInformation()
                        sal_ct_exp = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="job-detail__info--sections"]//div[@class="job-detail__info--section"]//div[@class="job-detail__info--section-content-value"]'))
                        )
                        details_infor.salary = sal_ct_exp[0].text
                        details_infor.city = sal_ct_exp[1].text
                        details_infor.yoe = sal_ct_exp[2].text

                        # deadline submit cv
                        try:
                            deadline = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="job-detail__info--deadline"]'))
                            )
                            details_infor.deadline_submit = deadline.text
                        except Exception as e:
                            print(f'Not deadline submit found: {e}') 
                        # job tag
                        try:
                            job_tags = WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="job-tags"]//span'))
                            )
                            details_infor.main_industry = [job_tag.text for job_tag in job_tags]
                        except Exception as e:
                            print(f'Not job tag found: {e}')
                        # description, requirements
                        try:
                            descriptions =  WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//h3[text()="Mô tả công việc"]//ancestor::div[@class="job-description__item"]//div[@class="job-description__item--content"]'))
                            )
                            details_infor.description = descriptions.text
                        except Exception as e:
                            print(f'Not descriptions found: {e}')

                        try:
                            requirements =  WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//h3[text()="Yêu cầu ứng viên"]//ancestor::div[@class="job-description__item"]//div[@class="job-description__item--content"]'))
                            )
                            details_infor.requirements = requirements.text
                        except Exception as e:
                            print(f'Not requirements found: {e}')        
                        # work address
                        try:
                            work_address =  WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//h3[text()="Địa điểm làm việc"]//ancestor::div[@class="job-description__item"]//div[@class="job-description__item--content"]'))
                            )
                            details_infor.work_address = work_address.text
                        except Exception as e:
                            print(f'Not work address found: {e}')
                        
                        # company size
                        try:
                            company_size =  WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="job-detail__company--information"]//div[@class="job-detail__company--information-item company-scale"]//div[@class="company-value"]'))
                            )
                            details_infor.company_size = company_size.text
                        except Exception as e:
                            print(f'Not company size found: {e}')    
                        
                        # major field

                        try:
                            major_field =  WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="job-detail__company--information"]//div[@class="job-detail__company--information-item company-field"]//div[@class="company-value"]'))
                            )
                            details_infor.major_field = major_field.text
                        except Exception as e:
                            print(f'Not company size found: {e}')    

                        # general information
                        try:
                            general_information =  WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="box-general-content"]//div[@class="box-general-group-info-value"]'))
                            )
                            details_infor.level = general_information[0].text
                            details_infor.num_of_recruit = general_information[2].text
                            details_infor.work_form = general_information[3].text
                            details_infor.gender_require = general_information[4].text
                        except Exception as e:
                            print(f'General infor not found: {e}')
                        # skills list
                        try:
                            skils_list =  WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="box-category collapsed"]//div[@class="box-category-tags"]//a'))
                            )
                            details_infor.skills = [a.text for a in skils_list]
                        except Exception as e:
                            print(f'Not skill list found: {e}')        
                        # area
                        try:
                            area =  WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="box-category"]//div[@class="box-category-tags"]//span//a'))
                            )
                            details_infor.area = [span.text for span in area]
                        except Exception as e:
                            print(f'Not area found: {e}')        
                        # relation fields
                        try:
                            relation_fields =  WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="box-category"]//div[@class="box-category-tags"]//a'))
                            )
                            details_infor.relation_fields = [a.text for a in relation_fields[:len(relation_fields) - len(details_infor.area)]]
                        except Exception as e:
                            print(f'Not relation fields found: {e}')

                        yield {
                            'id': f'{idx}', 
                            'title': title,
                            'company_name': company_name,
                            'salary': details_infor.salary,
                            'city': details_infor.city,
                            'yoe': details_infor.yoe,
                            'deadline_submit': details_infor.deadline_submit,
                            'main_industry': details_infor.main_industry,
                            'description': details_infor.description,
                            'requirements': details_infor.requirements,
                            'work_address': details_infor.work_address,
                            'company_size': details_infor.company_size,
                            'major_field': details_infor.major_field,
                            'level': details_infor.level,
                            'num_of_recruit': details_infor.num_of_recruit,
                            'work_form': details_infor.work_form,
                            'gender_require': details_infor.gender_require,
                            'relation_fields': details_infor.relation_fields,
                            'skills': details_infor.skills,
                            'area': details_infor.area,
                            'update_time': update_time,
                            'remain_time': remain_time                            
                        }

                        # print(
                        #     'details_infor: ', 
                        #         details_infor.salary, ', ', 
                        #         details_infor.city, ', ',
                        #         details_infor.yoe, ', ',
                        #         details_infor.deadline_submit, ', ',
                        #         details_infor.main_industry, ', ',
                        #         details_infor.description, ', ',
                        #         details_infor.requirements, ', ',
                        #         details_infor.work_address, ', '

                        # )
                    except Exception as e:
                        print(f'Not enough 3 elements: {e}')
                except Exception as e:
                    print(f"Error when try to access link for details of '{idx}'")
        except Exception as e:
            yield {"Error: ", e}
        finally:
            driver.quit()
        
# https://www.zenrows.com/blog/selenium-cloudflare-bypass#seleniumbase