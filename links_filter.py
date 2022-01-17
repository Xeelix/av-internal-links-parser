from urllib.parse import urlparse, urljoin

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


def generate_filtered_file():
    all_links = set(open(FILE_NAME, 'r', encoding='utf-8').readlines())
    all_links = clear_repeating_links(all_links)
    all_links = remove_trailing_slash_in_list(all_links)
    all_links = filter_only_one_domain(all_links)


    with open("filtered_links.txt", "w") as f:
        for external_link in all_links:
            print(external_link.strip(), file=f)

    print("Filtering was successful")

generate_filtered_file()
