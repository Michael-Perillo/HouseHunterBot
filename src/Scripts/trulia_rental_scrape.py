import sys
import json
import pandas as pd

from src.Config.DRIVER_CACHE_DIRECTORY import CACHE_DIR
from src.Config.RENTAL_URLS import URL_DICT
from src.Config.RENTAL_DATA_CONFIG import TRULIA_FIRST_HEADERS, TRULIA_HOUSE_METRICS_ATTRS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup, Tag

def home_highlights_location(tag: Tag) -> bool:
    RELEVANT_ATTR = 'data-testid'
    RELEVANT_ATTR_VAL = 'styled-section-container-heading'
    if tag.name == 'h3' and tag.has_attr(RELEVANT_ATTR):
        if tag.attrs[RELEVANT_ATTR] == RELEVANT_ATTR_VAL:
            if tag.text == 'Home Highlights':
                return True
    return False


def home_highlights_cell_location(tag: Tag) -> bool:
    if tag.name == 'div' and tag.attrs['class'][0].find('Grid__CellBox') != -1:
        return True
    return False


def home_highlights_next_entry_location(tag: Tag) -> bool:
    if tag.name == 'div' and tag.attrs['class'][0].find('Text__TextBase') != -1:
        return True
    return False


def parse_home_highlights(soup: BeautifulSoup) -> dict[str, str]:
    highlights_element = soup.find(home_highlights_location)
    cell = highlights_element.find_next(home_highlights_cell_location)
    out_dict = {}
    while cell is not None:
        cell_data = cell.find_all(home_highlights_next_entry_location)
        key_value_pair = [t.text for t in cell_data]
        cell_key, cell_value = key_value_pair[0], key_value_pair[1]
        out_dict[cell_key] = cell_value
        cell = cell.find_next_sibling()
    return out_dict


def appliance_header_location(tag: Tag) -> bool:
    return tag.name == 'div' \
           and tag.attrs.get('data-testid') is None \
           and tag.attrs.get('class') is not None \
           and tag.attrs['class'][0].find('Text__TextBase') != -1 \
           and tag.text.find('Appliances') != -1



def find_appliances_html(soup: BeautifulSoup) -> Tag:
    """
    Return the cells listing the appliances
    :param soup: Soup object representing the home's page
    :return: The first span tag in the group of appliances
    """
    return soup.find(appliance_header_location).find_next('span')

def parse_appliances(soup: BeautifulSoup) -> list:
    appliance_tag = find_appliances_html(soup)
    out_list = []
    while appliance_tag is not None:
        out_list.append(appliance_tag.text)
        appliance_tag = appliance_tag.find_next_sibling()
    return out_list


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
    driver.quit()
    # Now, we want to get information about individual addresses, so look up the urls individually and parse them
    for url in prelim_dataframe.url:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(path=CACHE_DIR).install()))
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Get rent:
        rent_div = soup.find('h3', attrs=TRULIA_HOUSE_METRICS_ATTRS['h3-data'])
        rent_numeric = int(rent_div.findChild().text.split('/')[0].replace('$', '').replace(',', ''))
        # Get square feet:
        sq_ft_image = soup.find('img', attrs=TRULIA_HOUSE_METRICS_ATTRS['sqft'])
        sq_ft_numeric = int(sq_ft_image.find_next_sibling().text.split()[0].replace(',', ''))
        # Get number of beds:
        beds_image = soup.find('img', attrs=TRULIA_HOUSE_METRICS_ATTRS['beds'])
        beds_numeric = int(beds_image.find_next_sibling().text.split()[0])
        # Get number of baths:
        baths_image = soup.find('img', attrs=TRULIA_HOUSE_METRICS_ATTRS['baths'])
        baths_numeric = float(baths_image.find_next_sibling().text.split()[0])
        home_highlights_dict = parse_home_highlights(soup)
        appliances_list = parse_appliances(soup)







    print('done')


if __name__ == '__main__':
    sys.exit(main())
