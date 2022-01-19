import re
import time
from urllib.parse import urlparse
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from __colors__.colors import *

from main import target_domain, files_folder, GRAY

success = 0
failed = 0
undefined_links = 0

# Links from test cases
categories_without_tailing = [
    "brands",  # 1
    "collections",  # 3
]

categories_with_tailing = [
    "i",  # 2
    "catalog",  # 4
    "ideas",  # 5
    "shops",  # 5
    "about",  # 5
    "tort",  # 5
]

# 9
custom_urls_to_watch = {
    f"https://{target_domain}/food/all/": f"https://{target_domain}/catalog",
    f"https://{target_domain}/.htpasswd": f"https://{target_domain}/",
    f"https://{target_domain}/.htpasswd'": f"https://{target_domain}/",
    f"https://{target_domain}/.nsconfig": f"https://{target_domain}/",
    f"https://{target_domain}/...": f"https://{target_domain}/",
    f"https://{target_domain}/.rhosts": f"https://{target_domain}/",
    f"https://{target_domain}/.bootstraprc": f"https://{target_domain}/",
    f"https://{target_domain}/.htaccess": f"https://{target_domain}/",
    f"https://{target_domain}/.subversion": f"https://{target_domain}/",
    f"https://{target_domain}/.bashrc": f"https://{target_domain}/",
    f"https://{target_domain}/.gist": f"https://{target_domain}/",
}


def read_links(filename):
    links_array = []
    with open(f"{files_folder}/{filename}", 'r') as inputfile:
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


# Get right link
def link_rules(actual_link):
    parsed_url = urlparse(actual_link)
    splitted_url = parsed_url.path.split("/")
    splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))  # Filter empty

    expected_link = None
    # Rule for https://av.ru
    if len(splitted_url_paths) <= 0:
        if len(splitted_url) >= 1:
            expected_link = f"{parsed_url.scheme}://{parsed_url.hostname}"
    # Else if path more that one [https.av.ru/first/third/...]
    else:
        # If path without / on end
        if splitted_url_paths[0] in categories_without_tailing:
            expected_link = delete_repeating_trailings(actual_link)
        # If path with / on end
        elif splitted_url_paths[0] in categories_with_tailing:
            actual = delete_repeating_trailings(actual_link)
            expected_link = add_end_trailing(actual)
    return expected_link


def check_link(driver, link_from_file):
    global success
    global failed
    global undefined_links

    isCustom = False
    expected_link = None

    driver.get(link_from_file)
    actual_link = driver.current_url

    if link_from_file in custom_urls_to_watch:
        expected_link = custom_urls_to_watch[link_from_file]
        isCustom = True
    else:
        expected_link = link_rules(actual_link)

    if expected_link is None:
        print(GRAY + "[?] " + f'Undefined Link: {actual_link}')
        undefined_links += 1
        return

    if actual_link != expected_link:
        print(fr + "[-] " + f'Test failed:\n\texpected: {expected_link}\n\tactual: {actual_link}')
        failed += 1
    else:
        if isCustom: expected_link = link_from_file
        print(fg + "[+] " + f'Test success:\n\texpected: {expected_link}\n\tactual: {actual_link}')
        success += 1

    return expected_link


def start_tests():
    all_links = read_links('filtered_links.txt')
    # all_links = ["https://av.ru/.htpasswd", "https://av.ru/collections/gift_tea_sets/", "https://av.ru",
    #              "https://av.ru", "https://av.rus/"]

    driver = initialize_driver()
    driver.set_page_load_timeout(20)
    # driver = 123

    for link in all_links:
        if link[-1] == "\n":
            link = link[:-1]
        try:
            check_link(driver, link)
        except TimeoutException as e:
            print(fr + "[-] " + f'Test failed:\n\tTimeoutException: {link}')
            continue
        except Exception as e:
            print(e)
            continue

    print("\n")
    print("Result: ")
    print(fg + f'Successfully: {success}')
    print(fr + f'Failed: {failed}')
    print(GRAY + f'Undefined: {undefined_links}')
    print(f'Total: {failed + success + undefined_links}')


# start_tests()
if __name__ == "__main__":
    start_time = datetime.now()

    start_tests()

    print("[?] Taken time:", datetime.now() - start_time)
#
# @pytest.fixture()
# def some_data():
#     """Return answer to ultimate question."""
#     return 42
#
#
# def test_some_data(some_data):
#     """Use fixture return value in a test."""
#     assert some_data == 42
