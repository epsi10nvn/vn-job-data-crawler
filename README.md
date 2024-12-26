1. Create venv by conda
   conda create -n <name_env> python=3.12.7

2. Activate
   conda activate <name_env>

3. Pip install
   pip install -r requirements.txt

4. Run scrapy
   scrapy crawl topcv -o data_output/topcv.json
