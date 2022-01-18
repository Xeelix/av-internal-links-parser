from urllib.parse import urlparse, urljoin

from selenium_test import add_end_trailing, custom_urls_to_watch

FILE_NAME = "file_result.txt"
MAX_REPEATS_COUNT = 4

categories_repeats = {
    "/i/": 0,
    "/g/": 0,
    "/files/": 0,
    "/catalog/": 0,
    "/collections/": 0,
    # "/ideas/": 0,
    "/brands/": 0,
    "/news/": 0,
    "/press/": 0,
    "/about/": 0,
    "/upload/": 0,
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


def find_main_route_in_path(url):
    detect_by_first = [
        "catalog",
        "upload",
        "files",
        # "ideas",
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

    test = "https://av.ru/about/tenders/"
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
        if link[len(link) - 1] == "/":
            link = link[:-1]
        new_list.append(link)
    return new_list


def filter_only_one_domain(links):
    target_hostname = "av.ru"
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

    for link in links:
        parsed_url = urlparse(link)
        splitted_url = parsed_url.path.split("/")
        splitted_url_paths = list(filter(lambda x: len(x) > 0, splitted_url))  # Filter empty

        if len(splitted_url_paths) >= 1:
            if splitted_url_paths[0] in categories_with_tailing:
                link = add_end_trailing(link)
        else:
            link = add_end_trailing(link)

        output_links.append(link)

    return output_links


def add_custom_urls_to_array(links):
    for watched in custom_urls_to_watch:
        links.append(watched)
    return links


def generate_filtered_file():
    all_links = set(open(FILE_NAME, 'r', encoding='utf-8').readlines())
    all_links = clear_repeating_links(all_links)
    all_links = remove_trailing_slash_in_list(all_links)
    all_links = set(filter_only_one_domain(all_links))
    all_links = set_links_by_rules(all_links)
    all_links = add_custom_urls_to_array(all_links)

    with open("filtered_links.txt", "w") as f:
        for external_link in all_links:
            print(external_link.strip(), file=f)

    print("Filtering was successful")


generate_filtered_file()
