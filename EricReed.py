from bs4 import BeautifulSoup
import requests
import re
from bs4.element import Comment


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def words_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.find_all(string=True)
    visible_texts = filter(tag_visible, texts)
    text_string = " ".join(t for t in visible_texts)
    words = re.findall(r'\w+', text_string)
    return words


def text_harvester(url):
    headers = {
        'User-Agent': ''}
    try:
        page = requests.get(url, headers=headers)
    except:
        return []
    res = words_from_html(page.content)

    return res

print(text_harvester('http://foothill.edu'))