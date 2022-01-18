import codecs
from datetime import datetime
import time
from multiprocessing import Pool

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
from threading import Thread

# init the colorama module
from requests import ConnectTimeout
from urllib3.exceptions import ConnectTimeoutError

target_domain = "stage.av.ru"

colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED

THREADS_COUNT = 10

# initialize the set of links (unique links)
internal_urls = set()
internal_urls_dict = []
external_urls = set()
globalData = set()

isProductParsed = False

total_urls_visited = 0

MAX_PRODUCTS_TO_VISIT = 1
visited_products = 0

skipped = [
    "/catalog/",
    "/upload/",
    "/g/",
    "/brands/"
    "/about/",
    "/demo/",
    "/i/"
]


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    global isProductParsed
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url, timeout=(6.05, 10)).content, "html.parser")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        # if isProductParsed:
        #     continue
        if "/i/" in href:
            isProductParsed = True
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")

        urls.add(href)
        internal_urls.add(href)
        internal_urls_dict.append(href)

        with open(f"{target_domain}_after.txt", "a") as f:
            for internal_link in urls:
                print(internal_link.strip(), file=f)
    return urls


def crawl(url, max_urls=40):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited, visited_products

    for itemCatalog in skipped:
        if itemCatalog in url:
            if "/i/" in url and visited_products < MAX_PRODUCTS_TO_VISIT:
                visited_products += 1
                continue
            else:
                return

    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    try:
        links = get_all_website_links(url)
        for link in links:
            globalData.add(link)
            if total_urls_visited > max_urls:
                break
            # if link in internal_urls or link in external_urls:
            #     continue
            # if "/i/" in link and isProductParsed:
            #     continue
            if link == "https://stage.av.ru/about/daily/":
                pass

            crawl(link, max_urls=max_urls)
    except Exception as e:
        print(f"{RED}[!] Timeout error for link {url}{RESET}")


if __name__ == "__main__":
    start_time = datetime.now()

    # save the external links to a file
    with open(f"{target_domain}_after.txt", "w") as f:
        print(f"{GRAY}[+] File was updated{RESET}")

    url = f"https://{target_domain}"
    max_urls = 50

    all_base_links = get_all_website_links(url)

    with Pool(THREADS_COUNT) as p:
        p.map(crawl, all_base_links)

    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls))
    print("[+] Total crawled URLs:", max_urls)

    domain_name = urlparse(url).netloc

    # save the internal links to a file
    with open(f"{domain_name}_internal_links.txt", "w") as f:
        for internal_link in internal_urls:
            print(internal_link.strip(), file=f)

    # save the external links to a file
    with open(f"{domain_name}_external_links.txt", "w") as f:
        for external_link in external_urls:
            print(external_link.strip(), file=f)

    # save the external links to a file
    with open(f"{domain_name}_global.txt", "w") as f:
        for external_link in globalData:
            print(external_link.strip(), file=f)

    uniqlines = set(open(f"{target_domain}_after.txt", 'r', encoding='utf-8').readlines())
    done_file = open("file_result.txt", 'w', encoding='utf-8').writelines(set(uniqlines))

    print("[?] Taken time:", datetime.now() - start_time)
