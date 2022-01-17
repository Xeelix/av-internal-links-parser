import re
import time
from urllib.parse import urlparse, urljoin

from __colors__.colors import *

from selenium import webdriver


def read_links(filename):
    links_array = []
    with open(filename, 'r') as inputfile:
        for line in inputfile:
            links_array.append(line)

    return links_array


def initialize_driver():
    fp = open('prefBrowser.txt', 'r')
    typex = fp.read()

    try:
        driver = None
        # For Chrome
        if typex == 'chrome':
            driver = webdriver.Chrome(executable_path=r'./webdriver/chromedriver')
        # For Firefox
        elif typex == 'firefox':
            # cap = DesiredCapabilities().FIREFOX
            # cap['marionette'] = True
            driver = webdriver.Firefox(executable_path=r'./webdriver/geckodriver')
        elif typex == '':
            print(fr + 'Error - Run setup.py first')
            exit()

        return driver
    except Exception as e:
        time.sleep(0.4)
        print('\n' + fr + 'Error - ' + str(e))
        exit()


def delete_repeating_trailings(link):
    parsed_link = urlparse(link)
    path = urlparse(link).path

    normalized_path = re.sub(r"(/{2,})", "/", path)
    normalized_link = f"{parsed_link.scheme}://{parsed_link.hostname}{normalized_path}"
    normalized_link = normalized_link.rstrip("/")

    return normalized_link


def add_end_trailing(link):
    result = link
    if link[:-1] != "/":
        result += "/"
    return result


def link_rules(actual_link):
    parsed_url = urlparse(actual_link)
    splitted_url = parsed_url.path.split("/")
    splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))

    delete_repeating_trailings(actual_link)

    # Rule for https://av.ru
    if len(splitted_url_paths) <= 0:
        if len(splitted_url) >= 1:
            delete_repeating_trailings(actual_link)
            return f"{parsed_url.scheme}://{parsed_url.hostname}"


def check_link(driver, link):
    # driver.get(link)
    # actual_url = driver.current_url
    actual_url = link

    test = link_rules(actual_url)
    pass


def start_tests():
    # all_links = read_links('filtered_links.txt')
    all_links = ["https://av.ru/"]

    # driver = initialize_driver()
    driver = 123

    for link in all_links:
        check_link(driver, link)


start_tests()
