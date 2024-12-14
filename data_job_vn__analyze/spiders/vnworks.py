import time
import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class JobDetailsInformation():
    def __init__(self):
        self.inside_title = None
        self.salary = "Nagotiation"
        self.position = None
        self.by_expiration_date = None
        self.views = 0
        self.city = None

        self.description = None
        self.requirements = None

        self.posted_date = None
        self.level = None
        self.field = None
        self.skills = None
        self.main_industry = None
        self.cv_language = None
        self.yoe = None

        self.work_address = None
        self.company_name = None
        self.company_size = None
        self.key_words = list()

class VnworksSpider(scrapy.Spider):
    name = "vnworks"
    allowed_domains = ["www.vietnamworks.com"]
    start_urls = ["https://www.vietnamworks.com/"]
    key_word = 'data'

    def start_requests(self):
        url = self.start_urls[0]
        yield SeleniumRequest(url=url, wait_time=3, callback=self.parse)

    def parse(self, response):
        driver = webdriver.Chrome()
        driver.set_window_size(1920, 1080)

        try:
            driver.get("https://www.vietnamworks.com/")
            time.sleep(3)
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-koXPp ctrWTa"]//input[@class="sc-iHGNWf gTcRnk  class-input-recommend"]'))
            )
            search_box.clear()
            search_box.send_keys(self.key_word)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            related_nav = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-35d7863d-0 VPzFI"]//div[text()="Liên quan nhất"]'))
            )
            related_nav.click()
            time.sleep(3)

            '''
            Get outside information
            '''
            # num_navs = len(driver.find_elements(By.XPATH, '//div[@class="sc-62971003-0 fkwXHN"]//ul//li'))
            num_navs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="sc-62971003-0 fkwXHN"]//ul//li'))
            )
            idx = 0
            details_link = {}
            for np in range(len(num_navs)):
                print(f"Current i: {np}")
                button_nav = driver.find_element(By.XPATH, f'//div[@class="sc-62971003-0 fkwXHN"]//ul//li//button[text()="{np + 1}"]')
                button_nav.send_keys(Keys.RETURN)
                time.sleep(5)

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

                time.sleep(5)
                job_blocks = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.search_list.view_job_item.new-job-card'))
                )
                for i, job in enumerate(job_blocks):
                    try:
                        job_title = job.find_element(By.XPATH, './/div[@class="sc-dYoqmx jdwsGi"]//h2//a')
                        # Tìm thẻ <span> bên trong thẻ <a>
                        job_title_text = job_title.text
                        
                        try:
                            span_element = job_title.find_element(By.TAG_NAME, 'span')
                            span_text = span_element.text
                            job_title_text = ' '.join(job_title_text.split()[len(span_text.split()):])
                        except Exception:
                            span_text = None  # Nếu không có <span> thì giá trị là None

                        details_link[idx] = {'href': job_title.get_attribute('href'), 'title': job_title_text, 'post_tag': span_text}
                        idx += 1
                    
                    except Exception as e:
                        print(f'Lỗi khi lấy thông tin từ trang {np}, job {i}: {e}')
                        yield {f'Lỗi khi lấy thông tin từ trang {np}, job {i}: {e}'}
            
            
            '''
                Get details information for each job post            
            '''
            # print(details_link)
            for idx, data in details_link.items():
                # if idx == 2:
                #     break
                href = data['href']
                outside_title = data['title']
                post_tag = data['post_tag']

                try: 
                    driver.get(href)
                    time.sleep(5)
                    try:
                        try:
                            more_detail_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-4913d170-0 gtgeCm"]//button[text()="Xem đầy đủ mô tả công việc"]'))
                            )
                            more_detail_button.send_keys(Keys.RETURN)
                            time.sleep(3)
                        except Exception as e:
                            yield {'No more detail button found!'}
                        '''
                        Get all details information
                        '''
                        details_infor = JobDetailsInformation()
                        # inside title
                        details_infor.inside_title = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@class="sc-335c0d9a-7 bByzUV"]//p[@class="sc-df6f4dcb-0 bsKseP sc-335c0d9a-8 bvFcVq"]'))
                        )
                        details_infor.inside_title = details_infor.inside_title.text
                        # salary and position
                        sal_pos = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 djNogb"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 lmzgIo"]//span'))
                        )
                        
                        details_infor.salary = sal_pos[0].text if sal_pos[0].text != 'Thương lượng' else 'Nagotiation'
                        if len(sal_pos) == 2:
                            details_infor.position = sal_pos[1].text
                        # by expiration date, view, city
                        di_day_view_city = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 dnguBj"]//div[@class="sc-8868b866-0 cbTySJ"]//span'))
                        )
                        details_infor.by_expiration_date = di_day_view_city[0].text
                        details_infor.views = di_day_view_city[1].text
                        details_infor.city = di_day_view_city[2].text

                        # descriptions and requirements details
                        des_req = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="sc-4913d170-3 hOVYfk"]//div[@class="sc-4913d170-4 jSVTbX"]//div[@class="sc-4913d170-6 hlTVkb"]'))
                        )
                        details_infor.description = des_req[0].text
                        details_infor.requirements = des_req[1].text

                        # posted_date
                        details_infor.posted_date = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="NGÀY ĐĂNG"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.posted_date = details_infor.posted_date.text

                        # level
                        details_infor.level = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="CẤP BẬC"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.level = details_infor.level.text

                        # field
                        details_infor.field = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="NGÀNH NGHỀ"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.field = details_infor.field.text

                        # skills
                        details_infor.skills = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="KỸ NĂNG"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.skills = details_infor.skills.text

                        # main_industry
                        details_infor.main_industry = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="LĨNH VỰC"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.main_industry = details_infor.main_industry.text

                        # cv_language
                        details_infor.cv_language = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="NGÔN NGỮ TRÌNH BÀY HỒ SƠ"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.cv_language = details_infor.cv_language.text

                        # yoe
                        details_infor.yoe = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@id="vnwLayout__row" and @class="sc-b8164b97-0 MfuTs"]//div[@id="vnwLayout__col" and @class="sc-8868b866-0 GVIEn"]//label[text()="SỐ NĂM KINH NGHIỆM TỐI THIỂU"]//ancestor::div[@class="sc-7bf5461f-2 JtIju"]//p'))
                        )
                        details_infor.yoe = details_infor.yoe.text

                        # work_address
                        details_infor.work_address = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//ancestor::h2[text()="Địa điểm làm việc"]//ancestor::div[@class="sc-a137b890-0 bAqPjv"]//div//p'))
                        )
                        details_infor.work_address = details_infor.work_address.text

                        # key words
                        key_words = WebDriverWait(driver, 5).until(
                            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="vnwLayout__col" and @class="sc-8868b866-0 ivdgrd"]//div[@class="sc-a3652268-3 esrWRf"]//span'))
                        )
                        for key in key_words:
                            details_infor.key_words.append(key.text)

                        # company_name
                        try:
                            company_name = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-37577279-0 joYsyf"]//a[@class="sc-df6f4dcb-0 dIdfPh sc-f0821106-0 gWSkfE"]'))
                            )
                            details_infor.company_name = company_name.text
                        except Exception as e:
                            print("Company name not found!")

                        # company_size
                        try:
                            company_size = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@class="sc-37577279-0 joYsyf"]//span[text()="nhân viên"]'))
                            )
                            details_infor.company_size = company_size.text
                        except Exception as e:
                            print("Company size not found!")
                        
                        yield {
                            'id': idx,
                            'title': outside_title, 
                            'post_tag': post_tag,
                            'inside_title': details_infor.inside_title,
                            'salary': details_infor.salary, 
                            'position': details_infor.position,
                            'by_expiration_date': details_infor.by_expiration_date, 
                            'views': details_infor.views, 
                            'city': details_infor.city, 
                            'description': details_infor.description,
                            'requirements': details_infor.requirements,
                            'posted_date': details_infor.posted_date, 
                            'level': details_infor.level,
                            'field': details_infor.field, 
                            'skills': details_infor.skills,
                            'main_industry': details_infor.main_industry,
                            'cv_language': details_infor.cv_language, 
                            'yoe': details_infor.yoe,
                            'work_address': details_infor.work_address,
                            'key_words': details_infor.key_words,
                            'company_name': details_infor.company_name,
                            'company_size': details_infor.company_size
                        }
                        
                    except Exception as e:
                        yield {f"Something went wrong when crawl details information: {e}"}
                except Exception as e:
                    yield {f"Error when try to access link for details of '{details_link[idx]}'"}
        except Exception as e:
            yield {"Error: ", e}
        finally:
            
            driver.quit()
# https://www.zenrows.com/blog/scrapy-selenium#interact-with-web-pages
