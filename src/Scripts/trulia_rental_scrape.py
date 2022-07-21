import sys
import json
import pandas as pd

from src.Config.DRIVER_CACHE_DIRECTORY import CACHE_DIR
from src.Config.RENTAL_URLS import URL_DICT
from src.Config.RENTAL_DATA_CONFIG import TRULIA_FIRST_HEADERS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup





def main():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(path=CACHE_DIR).install()))
    driver.get(URL_DICT['TRULIA'])
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')
    tag_with_listings = soup.find('script', type='application/ld+json')
    listings = json.loads(str(tag_with_listings.string))['@graph'][0]['about']
    # Build preliminary frame of listings which we use to get more information later
    prelim_dataframe = pd.DataFrame(columns=TRULIA_FIRST_HEADERS)
    for listing_container in listings:
        # Get the dict containing the address info
        listing = listing_container['address']
        data = []
        for header in TRULIA_FIRST_HEADERS[:-1]:
            # Extract address
            data.append(listing[header])
        # Finally, extract URL from listing container, prepend the base url to allow for easily accessing later
        data.append('https://www.trulia.com' + listing_container['url'])
        # Build the dataframe of address/url data row wise
        insert = pd.Series(data=data, index=TRULIA_FIRST_HEADERS)
        prelim_dataframe = prelim_dataframe.append(insert, ignore_index=True)

    # Now, we want to get information about individual addresses, so look up the urls individually and parse them



    print('done')


if __name__ == '__main__':
    sys.exit(main())
