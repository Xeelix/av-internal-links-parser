import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import time
 
ignore = ['@', 'mail']
 
url = 'https://stage.av.ru/'
r = requests.get(url)
 
soup = BeautifulSoup(r.text, 'lxml')
 
#Получаем список ссылок с главной страницы
list_urls = []
for i in soup.findAll('a'):
    link = str(i.get('href'))
    list_urls.append(link)
 
uniq_list_links = list(OrderedDict.fromkeys(list_urls).keys())
links_of_pages = []
count = 1
for x in list_urls:
    get_x = requests.get(url + x)
    bsoup = BeautifulSoup(get_x.text, 'lxml')
    all_hrefs = bsoup.findAll('a')
    for link in all_hrefs:
        if "/i/" in link:
            continue
        if link not in uniq_list_links:
            links_of_pages.append(url + str(link.get('href')))
            print(count)
            count += 1
        else:
            continue
        
print(len(links_of_pages))
print(list(OrderedDict.fromkeys(links_of_pages).keys()))