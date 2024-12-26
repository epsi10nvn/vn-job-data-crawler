---
# **Vietnam Data Job Market Crawler with Scrapy and Selenium**

This project is designed to scrape job-related data from **VietnamWorks**, **TopCV**, and **LinkedIn**. The data is extracted using **Scrapy** and **Selenium**, and for LinkedIn, it leverages the **ScrapingDog API** to bypass restrictions. After scraping, the data can be stored in a **SQL Server Database** using **pyodbc** for further analysis.
---

## **Features**

- Scrape job postings and associated data from **VietnamWorks**, **TopCV**, and **LinkedIn**.
- Leverage **ScrapingDog API** to handle LinkedIn data with minimal restrictions.
- Store the scraped data into a **SQL Server Database** for structured processing.

---

## **Prerequisites**

1. Install dependencies from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a free account on [ScrapingDog](https://api.scrapingdog.com/) and obtain an API key for LinkedIn data scraping.

3. Ensure you have a valid SQL Server database setup with appropriate credentials if you wish to store data in the database.

---

## **Usage**

### **1. Setting Up the Project**

- Clone the repository and navigate to the project directory. Create a new virtual environment, for example:
  ```bash
  conda create -n <name_env> python=3.12.7
  conda activate <name_env>
  ```
- Update the Scrapy settings in `settings.py` to enable the pipeline:
  ```python
  ITEM_PIPELINES = {
      "data_job_vn__analyze.pipelines.DataJobVnAnalyzePipeline": 300,
  }
  ```

### **2. Running the Crawlers**

Each website has its own spider. Use the following commands to run the crawlers:

- For VietnamWorks:

  ```bash
  scrapy crawl vnworks -o data_output/vnworks.json
  ```

- For TopCV:

  ```bash
  scrapy crawl topcv -o data_output/topcv.json
  ```

- For LinkedIn (using ScrapingDog):
  ```bash
  scrapy crawl linkedin -o data_output/linkedin.json
  ```

**Note**: The XPath expressions used to extract elements rely on the HTML class names, which are subject to change. Ensure you update these expressions in the spiders for accurate scraping.

### **3. Pushing Data to SQL Server**

The `pipelines.py` file handles data insertion into the SQL Server database using **pyodbc**. Ensure the database connection details are correctly configured in `pipelines.py`.

---

## **Important Notes**

- **Dynamic Elements**: Many websites (e.g., VietnamWorks, TopCV) use dynamic content. If elements are not found during scraping, update the `XPath` or `CSS selectors` in the spiders.
- **API Key for LinkedIn**: Replace the placeholder API key in the LinkedIn spider with your ScrapingDog API key.

---

## **File Structure**

- **`spiders/`**: Contains individual spiders for VietnamWorks, TopCV, and LinkedIn.
- **`pipelines.py`**: Handles data processing and storage in SQL Server.
- **`settings.py`**: Contains project settings. Ensure `ITEM_PIPELINES` is enabled for data processing.
- **`requirements.txt`**: List of dependencies.

---

## **Future Enhancements**

- Extend support for more job platforms.

---

## **Usage of Crawled Data**

For a detailed explanation of how to use the crawled data for analysis, check out my blog post [here](https://vietngaitmode.wixsite.com/epsilon-data/post/mastering-data-analysis-techniques-with-powerbi).

## **Contributors**

Feel free to raise issues or contribute to this project. Your suggestions are always welcome!
