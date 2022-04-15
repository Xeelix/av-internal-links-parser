import multiprocessing
import requests
import colorama

import helper
import codecs
import shutil
import time
import sys
import os

from urllib3.exceptions import ConnectTimeoutError
from urllib.parse import urlparse, urljoin
from requests import ConnectTimeout
from multiprocessing import Pool
from datetime import datetime
from bs4 import BeautifulSoup
from threading import Thread

from helper import optimized_path

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED


class LinksParser:
    to_skip = [
        "/catalog/",
        "/upload/",
        "/g/",
        "/brands/"
        "/about/",
        "/demo/",
        "/i/"
    ]

    custom_paths_to_parse = [
        "tort"
    ]

    def __init__(self):
        self.internal_urls = set()
        self.internal_urls_dict = []
        self.external_urls = set()
        self.globalData = set()

        self.isProductParsed = False
        self.total_urls_visited = 0

        self.max_products_to_visit = 1
        self.max_urls = 50
        self.visited_products = 0

        self.target_domain = None
        self.url = None

    def set_target_domain(self, value):
        # TODO: Complete read from file target domains
        # self.target_domain = input("Paste target domain: ")
        self.target_domain = value

    def is_valid(self, url):
        """
        Checks whether `url` is a valid URL.
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def get_all_link_on_url(self, url):
        """
            Returns all URLs that is found on `url` in which it belongs to the same website
            """
        keyword = self.keyword_to_parse
        # all URLs of `url`
        # global isProductParsed, target_domain, total_urls_visited, visited_products
        urls = set()
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(
            url, timeout=(10, 15)).content, "html.parser")
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
            if not self.is_valid(href):
                # not a valid URL
                continue
            if href in self.internal_urls:
                # already in the set
                continue
            # if isProductParsed:
            #     continue
            if "/i/" in href:
                isProductParsed = True

            if keyword in href:
                msg = f"{keyword} [href] on {url}"
                print(msg)
                with open(optimized_path(os.path.join(helper.files_folder, helper.find_hrefs_path)),
                          "a") as f:
                    f.write(f"{msg}\n")

            if domain_name not in href:
                # external link
                if href not in self.external_urls:
                    print(f"{GRAY}[!] External link: {href}{RESET}")
                    self.external_urls.add(href)
                continue

            print(f"{GREEN}[*] Internal link: {href}{RESET}")

            urls.add(href)
            self.internal_urls.add(href)
            self.internal_urls_dict.append(href)

            with open(optimized_path(f"{helper.files_folder}/{self.target_domain}_after.txt"), "a") as f:
                for internal_link in urls:
                    print(internal_link.strip(), file=f)
        return urls

    def crawl(self, url, max_urls=40):
        """
        Crawls a web page and extracts all links.
        You'll find all links in `external_urls` and `internal_urls` global set variables.
        params:
            max_urls (int): number of max urls to crawl, default is 30.
        """

        for itemCatalog in self.to_skip:
            if itemCatalog in url:
                if "/i/" in url and self.visited_products < self.max_products_to_visit:
                    self.visited_products += 1
                    continue
                else:
                    return

        self.total_urls_visited += 1
        print(f"{YELLOW}[*] Crawling: {url}{RESET}")
        try:
            links = self.get_all_link_on_url(url)
            for link in links:
                self.globalData.add(link)
                if self.total_urls_visited > max_urls:
                    break
                # if link in internal_urls or link in external_urls:
                #     continue
                # if "/i/" in link and isProductParsed:
                #     continue
                if link == "https://stage.av.ru/about/daily/":
                    pass

                self.crawl(link, max_urls=max_urls)
        except Exception as e:
            print(f"{RED}[!] Timeout error for link {url}{RESET}")

    def parse(self):
        start_time = datetime.now()
        print(f"Pool count: {helper.threads_count}\n")

        target_domain = input("Input target domain: ")
        keyword_to_parse = input("Input keyword: ")

        self.keyword_to_parse = keyword_to_parse

        helper.check_directory_existing_and_create(helper.files_folder)

        # TODO: Realize to target domain fill
        self.set_target_domain(target_domain)

        with open(optimized_path(os.path.join(helper.files_folder, f"{self.target_domain}_after.txt")), "w") as f:
            print(f"{GRAY}[+] File was updated{RESET}")

        with open(optimized_path(os.path.join(helper.files_folder, helper.find_hrefs_path)), "w") as f:
            pass

        url = f"https://{self.target_domain}"
        first_wave_links = self.get_all_link_on_url(url)

        for route in self.custom_paths_to_parse:
            parsed = self.get_all_link_on_url(f"https://{self.target_domain}/{route}/")
            first_wave_links.update(parsed)
        all_data = []
        with Pool(helper.threads_count) as p:
            p.map(self.crawl, first_wave_links)

        print("[+] Total Internal links:", len(self.internal_urls))
        print("[+] Total External links:", len(self.external_urls))
        print("[+] Total URLs:", len(self.external_urls) + len(self.internal_urls))
        print("[+] Total crawled URLs:", self.max_urls)

        domain_name = urlparse(url).netloc

        # save the internal links to a file

        internal_links_path = os.path.join(
            helper.files_folder, f"{domain_name}_internal_links.txt")
        with open(optimized_path(internal_links_path), "w") as f:
            for internal_link in self.internal_urls:
                print(internal_link.strip(), file=f)

        # save the external links to a file
        external_links_path = os.path.join(
            helper.files_folder, f"{domain_name}_external_links.txt")
        with open(optimized_path(external_links_path), "w") as f:
            for external_link in self.external_urls:
                print(external_link.strip(), file=f)

        # save the external links to a file
        global_path = os.path.join(helper.files_folder, f"{domain_name}_global.txt")
        with open(optimized_path(global_path), "w") as f:
            for external_link in self.globalData:
                print(external_link.strip(), file=f)

        uniqlines = set(
            open(optimized_path(os.path.join(helper.files_folder, f"{self.target_domain}_after.txt")), 'r').readlines())
        done_file = open(optimized_path(os.path.join(
            helper.files_folder, helper.filename_parsed_links)), 'w').writelines(set(uniqlines))

        unique_keywords = set(
            open(optimized_path(os.path.join(helper.files_folder, helper.find_hrefs_path)), 'r').readlines())

        os.remove(optimized_path(os.path.join(helper.files_folder, helper.find_hrefs_path)))
        print("\nFound keywords:")
        for msg in unique_keywords:
            print(f"{msg}")
            with open(optimized_path(os.path.join(helper.files_folder, helper.find_hrefs_path)),
                      "a+") as f:
                f.write(f"{msg}")

        print("\n")

        os.remove(optimized_path(internal_links_path))
        os.remove(optimized_path(external_links_path))
        os.remove(optimized_path(global_path))
        os.remove(optimized_path(os.path.join(
            helper.files_folder, f"{self.target_domain}_after.txt")))

        print("[?] Taken time:", datetime.now() - start_time)


def print_info():
    print('''
target domain - Основной домен, на котором будет происходить поиск ссылок
keyword - Ключевое слово для поиска на странице
    ''')


if __name__ == "__main__":
    # Pyinstaller fix
    multiprocessing.freeze_support()
    print_info()

    lp = LinksParser()
    lp.parse()
