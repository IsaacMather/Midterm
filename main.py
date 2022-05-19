import timeit
import random
from random_words import RandomWords
from BST import BinarySearchTree
from hash_table import HashQP
from splay_tree import SplayTree
from AVL_tree import AVLTree
from bs4 import BeautifulSoup
import requests
import re
from bs4.element import Comment
from urllib.parse import urljoin

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
    print(link_list)
    return link_list


def link_fisher(url: str, depth=0, reg_ex=""):
        link_list = _link_fisher(url, depth, reg_ex)
        link_list = list(set(link_list))
        return link_list


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


class KeywordEntry:
    """Stores information about a specific word on a webpage

        Args:
            word (str): the word we're storing info about
            url (str): the url the word is located on
            location (int): location, where the word is on the page
    """

    def __init__(self, word: str, url: str = None, location: int = None):
        self._word = word.upper()
        if url:
            self._sites = {url: [location]}
        else:
            self._sites = {}

    def add(self, url: str, location: int) -> None:
        if url in self._sites:
            self._sites[url].append(location)
        else:
            self._sites[url] = [location]

    def get_locations(self, url: str) -> list:
        try:
            return self._sites[url]
        except IndexError:
            return []

    @property
    def sites(self) -> list:
        return [key for key in self._sites]

    def __lt__(self, other):
        if isinstance(other, str):
            other = other.upper()
            return self._word < other

        elif isinstance(other, KeywordEntry):
            return self._word < other._word

        else:
            print("Error, incorrect data type passed to __lt__")

    def __gt__(self, other):
        if isinstance(other, str):
            other = other.upper()
            return self._word > other

        elif isinstance(other, KeywordEntry):
            return self._word > other._word

        else:
            print("Error, incorrect data type passed to __gt__")

    def __eq__(self, other):
        if isinstance(other, str):
            other = other.upper()
            return self._word == other

        elif isinstance(other, KeywordEntry):
            return self._word == other._word

        else:
            print("Error, incorrect data type passed to __eq__")

    def __hash__(self):
        return hash(self._word)


class WebStore:

    def __init__(self, ds):
        self._store = ds()


    def crawl(self, url:str, depth:0, reg_ex=""):

        for link in link_fisher(url, depth,reg_ex):
            list_of_words = text_harvester(link)
            for location, word in enumerate(list_of_words):
                if len(word) < 4 or not word.isalpha():
                    continue
                if word in self._store:
                    keyword_object = self._store.find(word)
                    keyword_object.add(url, location)
                else:
                    keyword_to_store = KeywordEntry(word,link,location)
                    self._store.insert(keyword_to_store)


    def search(self, keyword: str):
        keyword_object = self._store.find(keyword)
        return keyword_object.sites()


    def search_list(self,kw_list: list):
        found = 0
        not_found = 0

        for keyword in kw_list:
            try:
                self.search(keyword)
                found += 1
            except:
                not_found += 1
                continue

        return (found, not_found)


    def crawl_and_list(self, url, depth=0, reg_ex=''):
        word_set = set()
        for link in link_fisher(url, depth, reg_ex):
            for word in text_harvester(link):
                if len(word) < 4 or not word.isalpha():
                    continue
                word_set.add(word)
        return list(word_set)


if __name__ == '__main__':
    rw = RandomWords()
    num_random_words = 5449
    search_trials = 10
    crawl_trials = 1
    structures = [BinarySearchTree, SplayTree, AVLTree, HashQP]
    for depth in range(4):
        print("Depth = ", depth)
        stores = [WebStore(ds) for ds in structures]
        known_words = stores[0].crawl_and_list("http://compsci.mrreed.com",
                                               depth)
        total_words = len(known_words)
        print(f"{len(known_words)} have been stored in the crawl")
        if len(known_words) > num_random_words:
            known_words = random.sample(known_words, num_random_words)
        num_words = len(known_words)
        random_words = rw.random_words(count=num_words)
        known_count = 0
        for word in random_words:
            if word in known_words:
                known_count += 1
        print(f"{known_count / len(random_words) * 100:.1f}% of random words "
              f"are in known words")
        for i, store in enumerate(stores):
            print("\n\nData Structure:", structures[i])
            time_s = timeit.timeit(
                f'store.crawl("http://compsci.mrreed.com", depth)',
                setup=f"from __main__ import store, depth",
                number=crawl_trials) / crawl_trials
            print(f"Crawl and Store took {time_s:.2f} seconds")
            for phase in (random_words, known_words):
                if phase is random_words:
                    print("Search is random from total pool of random words")
                else:
                    print("Search only includes words that appear on the site")
                for divisor in [1, 10, 100]:
                    list_len = max(num_words // divisor, 1)
                    print(f"- Searching for {list_len} words")
                    search_list = random.sample(phase, list_len)
                    store.search_list(search_list)
                    total_time_us = timeit.timeit(
                        'store.search_list(search_list)',
                        setup="from __main__ import store, search_list",
                        number=search_trials)
                    time_us = total_time_us / search_trials / list_len * (
                                10 ** 6)
                    found, not_found = store.search_list(search_list)
                    print(
                        f"-- {found} of the words in kw_list were found, out of "
                        f"{found + not_found} or "
                        f"{found / (not_found + found) * 100:.0f}%")
                    print(f"-- {time_us:5.2f} microseconds per search")
    print(f"{search_trials} search trials and "
          f"{crawl_trials} crawl trials were conducted")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
