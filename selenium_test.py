import re
import time
import links_filter
from urllib.parse import urlparse
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from __colors__.colors import *

import links_parser

success = 0
failed = 0
undefined_links = 0
errors_links = 0

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
    f"https://{links_parser.target_domain}/food/all/": f"https://{links_parser.target_domain}/catalog",
    f"https://{links_parser.target_domain}/.htpasswd": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.htpasswd'": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.nsconfig": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/...": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.rhosts": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.bootstraprc": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.htaccess": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.subversion": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.bashrc": f"https://{links_parser.target_domain}/",
    f"https://{links_parser.target_domain}/.gist": f"https://{links_parser.target_domain}/",
}


def read_links(filename):
    links_array = []
    with open(links_parser.optimized_path(f"{links_parser.files_folder}/{filename}"), 'r') as inputfile:
        for line in inputfile:
            links_array.append(line)

    return links_array


def initialize_driver():
    fp = open(links_parser.optimized_path('prefBrowser.txt'), 'r')
    typex = fp.read()

    try:
        driver = None

        # For Safari
        if typex == 'darwin':
            driver = webdriver.Safari()
        # For Chrome
        if typex == 'chrome':
            driver = webdriver.Chrome(executable_path=links_parser.optimized_path(r'./webdriver/chromedriver'))
        # For Firefox
        elif typex == 'firefox':
            # cap = DesiredCapabilities().FIREFOX
            # cap['marionette'] = True
            driver = webdriver.Firefox(executable_path=links_parser.optimized_path(r'./webdriver/geckodriver'))
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
    actual_link = actual_link.lower()
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


def check_link(driver, link_from_file, length_info):
    global success
    global failed
    global undefined_links

    isCustom = False
    expected_link = None

    driver.get(link_from_file)
    actual_link = driver.current_url

    parsed_url_from_file = urlparse(link_from_file)
    splitted_url_from_file = parsed_url_from_file.path.split("/")
    splitted_url_paths_from_file = list(filter(lambda x: len(x) > 0, splitted_url_from_file))  # Filter empty

    # If url - is custom
    if link_from_file in custom_urls_to_watch:
        expected_link = custom_urls_to_watch[link_from_file]
        isCustom = True
    # If /home or /index.php or /index in path
    elif splitted_url_paths_from_file[-1] in links_filter.categories_indexing:
        expected_link = link_rules(actual_link)
        isCustom = True
    else:
        expected_link = link_rules(actual_link)

    if expected_link is None:
        print(links_parser.GRAY + f"({length_info[0] + 1} of {length_info[1]}) [?] Undefined Link: {actual_link}")
        undefined_links += 1
        return

    expected_link = expected_link.lower()

    if actual_link != expected_link:
        print(
            fr + f"({length_info[0] + 1} of {length_info[1]}) [-] Test failed:\n\tincome: {link_from_file}\n\texpected: {expected_link}\n\tactual: {actual_link}")
        failed += 1
    else:
        if isCustom: expected_link = link_from_file
        print(
            fg + f"({length_info[0] + 1} of {length_info[1]}) [+] Test success:\n\tincome: {link_from_file}\n\texpected: {expected_link}\n\tactual: {actual_link}")
        success += 1

    return expected_link


def get_formatted_precent(value, count):
    percent = value * 100 / count
    return f"{percent: .0f}%"


def start_tests():
    global errors_links
    all_links = read_links('filtered_links.txt')

    driver = initialize_driver()
    driver.set_page_load_timeout(20)
    # driver = 123

    for index, link in enumerate(all_links):
        if link[-1] == "\n":
            link = link[:-1]
        try:
            check_link(driver, link, [index, len(all_links)])
        except TimeoutException as e:
            print(fr + f"({index + 1} of {len(all_links)}) [-] Test failed:\n\tTimeoutException: {link}")
            errors_links += 1
            continue
        except Exception as e:
            print(e)
            errors_links += 1
            continue

    print("\n")
    print("Result: ")
    print(fg + f'\tSuccessfully: {success} ({get_formatted_precent(success, len(all_links))})')
    print(fr + f'\tFailed: {failed} ({get_formatted_precent(failed, len(all_links))})')
    print(links_parser.GRAY + f'\tUndefined: {undefined_links} ({get_formatted_precent(undefined_links, len(all_links))})')
    print(fr + f'\tException links: {errors_links} ({get_formatted_precent(errors_links, len(all_links))})')
    print(f'\tTotal: {failed + success + undefined_links + errors_links}')


def start_test():
    start_time = datetime.now()

    start_tests()

    print("[?] Taken time:", datetime.now() - start_time)


# start_tests()
if __name__ == "__main__":
    start_test()
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
