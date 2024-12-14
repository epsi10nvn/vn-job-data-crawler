# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import datetime
import pyodbc
import logging

class DataJobVnAnalyzePipeline:
    def open_spider(self, spider):
        server = '192.168.1.69'
        database = 'data_job_vn_raw'
        username = 'epsilon_jr'
        password = '20112001'
        driver = '{ODBC Driver 17 for SQL Server}'

        connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

        self.connection = pyodbc.connect(connection_string)
        self.cursor = self.connection.cursor()

        # logging.info(spider.name)
        table_name = spider.name
        if table_name == 'vnworks':
            try:
                self.cursor.execute(f'''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
                    CREATE TABLE {table_name} (
                        id INT,
                        title NVARCHAR(255),
                        post_tag NVARCHAR(100),
                        salary NVARCHAR(100),
                        position NVARCHAR(100),
                        by_expiration_date NVARCHAR(255),
                        views NVARCHAR(100),
                        city NVARCHAR(100),
                        description NVARCHAR(MAX),
                        requirements NVARCHAR(MAX),
                        posted_date NVARCHAR(25),
                        level NVARCHAR(100),
                        field NVARCHAR(MAX),
                        skills NVARCHAR(MAX),
                        main_industry NVARCHAR(MAX),
                        cv_language NVARCHAR(100),
                        yoe NVARCHAR(100),
                        work_address NVARCHAR(255),
                        company_name NVARCHAR(255),                    
                        company_size NVARCHAR(255),
                        key_words NVARCHAR(MAX)
                    );
                ''')
                self.connection.commit()
            except Exception as e:
                print(f'Error when create vnworks table: {e}')
            # logging.log(f'Error when connect database: {e}')
        if table_name == 'topcv':
            table_name += '_new'
            try:
                self.cursor.execute(f'''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
                    CREATE TABLE {table_name} (
                        id INT,
                        title NVARCHAR(255),
                        company_name NVARCHAR(255),
                        salary NVARCHAR(100),
                        city NVARCHAR(100),
                        yoe NVARCHAR(100),
                        deadline_submit NVARCHAR(255),
                        main_industry NVARCHAR(MAX),
                        description NVARCHAR(MAX),
                        requirements NVARCHAR(MAX),
                        work_address NVARCHAR(255),
                        company_size NVARCHAR(255),
                        major_field NVARCHAR(MAX),
                        level NVARCHAR(100),
                        num_of_recruit NVARCHAR(100),
                        work_form NVARCHAR(100),
                        gender_require NVARCHAR(100),
                        relation_fields NVARCHAR(MAX),
                        skills NVARCHAR(MAX),
                        area NVARCHAR(MAX),                    
                        update_time NVARCHAR(255),
                        remain_time NVARCHAR(255)
                    );
                ''')
                self.connection.commit()
            except Exception as e:
                print(f'Error when create topcv table: {e}')

        if table_name == 'linkedin':
            try:
                self.cursor.execute(f'''
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
                    CREATE TABLE {table_name} (
                        job_id VARCHAR(255),
                        job_position NVARCHAR(255),
                        jobs_status NVARCHAR(100),
                        job_location NVARCHAR(255),
                        company_name NVARCHAR(255),
                        job_posting_time NVARCHAR(100),
                        base_pay NVARCHAR(MAX),
                        job_description NVARCHAR(MAX),
                        Seniority_level NVARCHAR(255),
                        Employment_type NVARCHAR(255),
                        Job_function NVARCHAR(255),
                        Industries NVARCHAR(255),
                        job_posting_date NVARCHAR(255)
                    );
                ''')
                self.connection.commit()
            except Exception as e:
                print(f'Error when create linkedin table: {e}')

    def close_spider(self, spider):
        self.connection.close()


    def process_item(self, item, spider):
        table_name = spider.name

        if spider.name == 'vnworks':
            key_words = item.get('key_words')
            str_key_words = ', '.join(key_words)
            self.cursor.execute(f'''
                INSERT INTO {table_name} (id, title, post_tag, salary, position, by_expiration_date, views, city, description, requirements, posted_date, level, field, skills, main_industry, cv_language, yoe, work_address, company_name, company_size, key_words)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                item.get('id'),
                item.get('title'),
                item.get('post_tag'),
                item.get('salary'),
                item.get('position'),
                item.get('by_expiration_date'),
                item.get('views'),            
                item.get('city'),
                item.get('description'),
                item.get('requirements'),
                item.get('posted_date'),
                item.get('level'),
                item.get('field'),
                item.get('skills'),
                item.get('main_industry'),
                item.get('cv_language'),
                item.get('yoe'),
                item.get('work_address'),
                item.get('company_name'),
                item.get('company_size'),
                str_key_words
            ))
            

        if spider.name == 'topcv':
            # main_industry
            main_industry = item.get('main_industry')
            str_main_industry = ', '.join(main_industry)
            # relation_fields
            relation_fields = item.get('relation_fields')
            str_relation_fields = ', '.join(relation_fields)
            # skills
            try:
                skills = item.get('skills')
                str_skills = ', '.join(skills)
            except Exception as e:
                str_skills = skills
                print(f'Can not join non-interable: {e}')
            # area
            area = item.get('area')
            str_area = ', '.join(area)
            table_name += '_new'
            self.cursor.execute(f'''
                INSERT INTO {table_name} (id, title, company_name, salary, city, yoe, deadline_submit, main_industry, description, requirements, work_address, company_size, major_field, level, num_of_recruit, work_form, gender_require, relation_fields, skills, area, update_time, remain_time)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                item.get('id'),
                item.get('title'),
                item.get('company_name'),
                item.get('salary'),
                item.get('city'),
                item.get('yoe'),
                item.get('deadline_submit'),
                str_main_industry,
                item.get('description'),            
                item.get('requirements'),
                item.get('work_address'),
                item.get('company_size'),
                item.get('major_field'),
                item.get('level'),
                item.get('num_of_recruit'),
                item.get('work_form'),
                item.get('gender_require'),
                str_relation_fields,
                str_skills,
                str_area,
                item.get('update_time'),
                item.get('remain_time')
            ))
        
        if spider.name == 'linkedin':
            self.cursor.execute(f'''
                INSERT INTO {table_name} (job_id, job_position, jobs_status, job_location, company_name, job_posting_time, base_pay, job_description, Seniority_level, Employment_type, Job_function, Industries, job_posting_date)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                item.get('job_id'),
                item.get('job_position'),
                item.get('jobs_status'),
                item.get('job_location'),
                item.get('company_name'),
                item.get('job_posting_time'),            
                item.get('base_pay'),
                item.get('job_description'),
                item.get('Seniority_level'),
                item.get('Employment_type'),
                item.get('Job_function'),
                item.get('Industries'),
                item.get('job_posting_date')
            ))
        self.connection.commit()
        return item
