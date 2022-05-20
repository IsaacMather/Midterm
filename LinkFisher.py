import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def _link_fisher(url: str, depth=0, reg_ex=""):
    link_list = []
    headers = {'User-Agent': ''}

    if depth == 0:
        link_list.append(url)
        return link_list

    try:
        page = requests.get(url, headers=headers)
    except:
        print("Cannot access page")
        return link_list

    if page.status_code >= 400:
        print("Page Error")

    data = page.text
    pattern = re.compile(reg_ex)

    soup = BeautifulSoup(data, features="html.parser")
    for link in soup.find_all('a'):
        link = link.get("href")
        if not pattern.match(link) or reg_ex == '':
            link = urljoin(url, link)
        link_list.append(link)
        link_list += _link_fisher(link, depth - 1, reg_ex)

    link_list.append(url)
    # print(link_list)
    return link_list


def link_fisher(url: str, depth=0, reg_ex=""):
        link_list = _link_fisher(url, depth, reg_ex)
        link_list = list(set(link_list))
        return link_list