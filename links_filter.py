import random
import re
import os
from urllib.parse import urlparse, urljoin

import links_parser
import selenium_test

# from selenium_test import add_end_trailing, custom_urls_to_watch

MAX_REPEATS_COUNT = 5

upper_case_count = -10

categories_repeats = {
    "/i/": -10,
    "/g/": 0,
    "/files/": 0,
    "/collections/": -10,
    "/brands/": 0,
    "/news/": 0,
    "/upload/": 0,
    "/press/": 0,
    "/catalog/": 0,
    "/ideas/": -20,
    "/shops/": 0,
    "/about/": -20,
    "/tort/": -10,
}

# generate Links for test
categories_with_tailing = [
    "brands",  # 1
    "collections",  # 3
]

categories_without_tailing = [
    "i",  # 2
    "catalog",  # 4
    "ideas",  # 5
    "shops",  # 5
    "about",  # 5
    "tort",  # 5
]

categories_indexing = {
    "index.php": 0,
    "index.html": 0,
    "home": 0,
}


def find_main_route_in_path(url):
    detect_by_first = [
        "catalog",
        "upload",
        "files",
        "tort",
        "ideas",
        "about",
    ]

    left_count = 2

    path = urlparse(url).path
    if path:
        if path[-1] != "/":
            path += "/"

    splitted = path.split("/")[1:-1]

    if len(splitted) <= 0:
        return "/"

    if splitted[0] in detect_by_first:
        return f"/{splitted[0]}/"

    path_len = len(splitted)

    route = splitted[path_len - 2]
    return f"/{route}/"


def clear_repeating_links(links):
    shorted_links = set()

    for link in links:
        link = link.rstrip()
        try:
            route = find_main_route_in_path(link)

            if route in categories_repeats:
                # current repeats count
                current_count = categories_repeats[route]
                # if count is max
                if current_count < MAX_REPEATS_COUNT:
                    categories_repeats[route] += 1
                    shorted_links.add(link)
            else:
                shorted_links.add(link)
        except Exception as e:
            print(f"{link} - {e}")
    return shorted_links


def remove_trailing_slash_in_list(links):
    new_list = []
    for link in links:
        if len(link) <= 0:
            continue
        if link[len(link) - 1] == "/":
            link = link[:-1]
        new_list.append(link)
    return new_list


def filter_only_one_domain(links):
    target_hostname = links_parser.target_domain
    target_scheme = "https"

    output_links = []
    for link in links:
        path = urlparse(link)
        if path.scheme == target_scheme and path.hostname == target_hostname:
            output_links.append(link)

    return output_links


def set_links_by_rules(links):
    """Generating links for tests"""
    output_links = []
    MAX_LINKS_WITH_TRAILING = 10
    links_with_trailings_count = 0

    for link in links:
        parsed_url = urlparse(link)
        splitted_url = parsed_url.path.split("/")
        splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))  # Filter empty

        if len(splitted_url_paths) >= 1:
            if splitted_url_paths[0] in categories_with_tailing:
                link = selenium_test.add_end_trailing(link)

            if (splitted_url_paths[0] in categories_without_tailing or splitted_url_paths[
                0] in categories_with_tailing) and links_with_trailings_count < MAX_LINKS_WITH_TRAILING:
                # Generating trailing
                generated_link = generate_trailing_link(parsed_url, splitted_url_paths)
                output_links.append(generated_link)
                links_with_trailings_count += 1
        else:
            link = selenium_test.add_end_trailing(link)

        if "tel:" in link:
            continue

        output_links.append(link)

    return output_links


def add_custom_urls_to_array(links):
    for watched in selenium_test.custom_urls_to_watch:
        links.append(watched)
    return links


def generate_trailing_link(parsed_url, splitted_url_paths):
    trailings = "/" * random.randint(2, 8)

    generated_path = ""
    for id, val in enumerate(splitted_url_paths):
        if id == 0:
            val += trailings
        generated_path += val + "/"

    generated_link = f"{parsed_url.scheme}://{parsed_url.hostname}/{generated_path}"
    return generated_link


def add_indexing_links_to_array(links):
    output_array = []

    for link in links:
        parsed_url = urlparse(link)
        splitted_url = parsed_url.path.split("/")
        splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))  # Filter empty

        isMultiTrailing = re.search(r"/{3,}", link)

        if isMultiTrailing:
            continue

        if len(splitted_url_paths) and splitted_url_paths[0] in categories_without_tailing:
            for index_category in categories_indexing:
                if categories_indexing[index_category] < MAX_REPEATS_COUNT:
                    generated_link = link
                    generated_link += f"/{index_category}"
                    output_array.append(generated_link)
                    categories_indexing[index_category] += 1

    links += output_array

    return links


def add_uppercase_links_to_array(links):
    global upper_case_count
    output_array = []

    for link in links:
        parsed_url = urlparse(link)
        splitted_url = parsed_url.path.split("/")
        splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))  # Filter empty

        isMultiTrailing = re.search(r"/{3,}", link)

        if isMultiTrailing:
            continue

        if upper_case_count < MAX_REPEATS_COUNT and len(splitted_url_paths) >= 1 and splitted_url_paths[0] != "i" and \
                splitted_url_paths[
                    0] in categories_without_tailing:
            upper_path = ""
            for i in parsed_url.path:
                if random.randint(0, 3) == 1:
                    i = i.upper()
                upper_path += i

            generated_uppercase_link = parsed_url.scheme + "://" + parsed_url.netloc + upper_path
            output_array.append(generated_uppercase_link)
            upper_case_count += 1

    links += output_array

    return links


def generate_filtered_file():
    print()
    all_links = set(open(links_parser.optimized_path(os.path.join(links_parser.files_folder, links_parser.FILENAME_PARSED_LINKS)), 'r').readlines())
    all_links = clear_repeating_links(all_links)
    all_links = remove_trailing_slash_in_list(all_links)
    all_links = set(filter_only_one_domain(all_links))
    all_links = set_links_by_rules(all_links)
    all_links = add_custom_urls_to_array(all_links)
    all_links = add_indexing_links_to_array(all_links)
    all_links = add_uppercase_links_to_array(all_links)


    with open(links_parser.optimized_path(os.path.join(links_parser.files_folder, "filtered_links.txt")), "w") as f:
        for external_link in all_links:
            print(external_link.strip(), file=f)

    print("Filtering was successful")


if __name__ == "__main__":
    generate_filtered_file()
