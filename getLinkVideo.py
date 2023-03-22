import pandas as pd
from dotenv import load_dotenv
import os
import logging
import progressbar

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup   

load_dotenv()

if not os.path.exists('./Crawl_data'):
    os.umask(0)
    os.makedirs('./Crawl_data', mode=0o777)

# Setup webdriver
options = webdriver.ChromeOptions() 
options.page_load_strategy = "normal"
driver = webdriver.Chrome(options=options)
progress = progressbar.ProgressBar()

# Path to save files
path = 'Crawl_data/'
USER_URL = 'https://www.douyin.com/user/MS4wLjABAAAAUx_0_1O2l2nScHoPafDfaCoaZ0Rh58qab7slIEJ66zg?vid=7064082656710888735'

limit = 50

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and set its level to ERROR
file_handler = logging.FileHandler(path+'error.log')
file_handler.setLevel(logging.ERROR)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Scroll the website to end in order to get all html tags
def scroll_to_end():
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

# Close ads if possible
def close_ads():
    try:
        ads = driver.find_element(By.CLASS_NAME,"dy-account-close")
        driver.execute_script("arguments[0].click();", ads) 
    except NoSuchElementException:
        return

# Wait for the dataTable to load
def wait_for_list_videos_to_load():
    try:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
    except Exception as e:
        logger.error('Failed to load dataTable from url: %s', e)

# Wait for the dataTable to load
def wait_for_download_link_to_load():
    try:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'EZC0YBrG'))
        )
    except Exception as e:
        logger.error('Failed to load dataTable from url: %s', e)

# Convert the crawl data to csv
def to_csv(list, name):
    df = pd.DataFrame(list)
    df.to_csv(path+name+'.csv') 

# Get data from the dataTable
def get_list_video(limit):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('ul',{'class':'EZC0YBrG'})
        data_rows = table.find_all('li')[:limit]
        return data_rows
    except Exception as e:
        logger.error('Failed to get dataTable from url: %s', e)

# Get data from the dataTable
def get_download_link_video():
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        body = soup.find('body')
        video = body.find('video')
        download_link = video.findAll('source')[2]
        return download_link['src'] # type: ignore
    except Exception as e:
        logger.error('Failed to get dataTable from url: %s', e)

# Get All data from row and convert to text
def get_video_link(row):
    row_texts = row.find('a', href=True)
    return row_texts['href'] # type: ignore

# Get page source from url
def get_url_page_source(url):
    try:
        driver.get(url)
    except Exception as e:
        logger.error('Failed to crawl from (%s): %s', url, e)

# Crawl data from single stock code
def crawl_single_user_tiktok_url():
    try:
        # Init a list to save temp data
        templist = []
        downLoadList = []
        get_url_page_source(USER_URL)
        input("After Verify, wait for the qr code to appear then press Enter to continue...")
        close_ads() 
        # scroll_to_end()
        wait_for_list_videos_to_load()

        for row in get_list_video(limit):
            templist.append(os.getenv('BASE_URL')+get_video_link(row))
                
        print('Getting download link, please wait ...')
        for link in progress(templist):
            get_url_page_source(link)
            # wait_for_download_link_to_load()
            downLoadList.append(get_download_link_video())
            
        to_csv(templist, 'link_video')
        to_csv(downLoadList, 'link_download_video')
    except Exception as e:
        logger.error('Failed to crawl data with code url: %s', e)

crawl_single_user_tiktok_url()
