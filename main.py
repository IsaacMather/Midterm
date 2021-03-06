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
    # print(link_list)
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
                try:
                    self._store.find(word)
                    keyword_object = self._store.find(word)
                    keyword_object.add(url, location)
                except self._store.NotFoundError:
                    keyword_to_store = KeywordEntry(word,link,location)
                    self._store.insert(keyword_to_store)


    def search(self, keyword: str):
        keyword_object = self._store.find(keyword)
        url_list = keyword_object.sites
        return url_list

    #why is it looping back around instead of retuning url list?


    def search_list(self,kw_list: list):
        found = 0
        not_found = 0

        for keyword in kw_list:
            try:
                found_item = self.search(keyword)
                found += 1
            except: #NotFoundError: we want a notfound error here, not bare
                # except
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
    results = {} #isaac ads
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
        #isaac ads

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

# Sample run
# /Users/isaacmather/PycharmProjects/Midterm/venv/bin/python /Users/isaacmather/PycharmProjects/Midterm/main.py
# Depth =  0
# 38 have been stored in the crawl
# 0.0% of random words are in known words
#
#
# Data Structure: <class 'BST.BinarySearchTree'>
# Crawl and Store took 0.06 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# -- 0 of the words in kw_list were found, out of 38 or 0%
# --  8.59 microseconds per search
# - Searching for 3 words
# -- 0 of the words in kw_list were found, out of 3 or 0%
# --  6.33 microseconds per search
# - Searching for 1 words
# -- 0 of the words in kw_list were found, out of 1 or 0%
# -- 13.42 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# -- 38 of the words in kw_list were found, out of 38 or 100%
# --  5.07 microseconds per search
# - Searching for 3 words
# -- 3 of the words in kw_list were found, out of 3 or 100%
# --  5.98 microseconds per search
# - Searching for 1 words
# -- 1 of the words in kw_list were found, out of 1 or 100%
# --  5.77 microseconds per search
#
#
# Data Structure: <class 'splay_tree.SplayTree'>
# Crawl and Store took 0.06 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# -- 0 of the words in kw_list were found, out of 38 or 0%
# -- 10.89 microseconds per search
# - Searching for 3 words
# -- 0 of the words in kw_list were found, out of 3 or 0%
# --  9.90 microseconds per search
# - Searching for 1 words
# -- 0 of the words in kw_list were found, out of 1 or 0%
# --  7.79 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# -- 38 of the words in kw_list were found, out of 38 or 100%
# -- 12.38 microseconds per search
# - Searching for 3 words
# -- 3 of the words in kw_list were found, out of 3 or 100%
# --  5.21 microseconds per search
# - Searching for 1 words
# -- 1 of the words in kw_list were found, out of 1 or 100%
# --  2.66 microseconds per search
#
#
# Data Structure: <class 'AVL_tree.AVLTree'>
# Crawl and Store took 0.06 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# -- 0 of the words in kw_list were found, out of 38 or 0%
# --  5.58 microseconds per search
# - Searching for 3 words
# -- 0 of the words in kw_list were found, out of 3 or 0%
# --  5.43 microseconds per search
# - Searching for 1 words
# -- 0 of the words in kw_list were found, out of 1 or 0%
# --  6.29 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# -- 38 of the words in kw_list were found, out of 38 or 100%
# --  4.51 microseconds per search
# - Searching for 3 words
# -- 3 of the words in kw_list were found, out of 3 or 100%
# --  8.27 microseconds per search
# - Searching for 1 words
# -- 1 of the words in kw_list were found, out of 1 or 100%
# -- 10.21 microseconds per search
#
#
# Data Structure: <class 'hash_table.HashQP'>
# Crawl and Store took 0.06 seconds
# Search is random from total pool of random words
# - Searching for 38 words
# -- 0 of the words in kw_list were found, out of 38 or 0%
# --  3.27 microseconds per search
# - Searching for 3 words
# -- 0 of the words in kw_list were found, out of 3 or 0%
# --  3.78 microseconds per search
# - Searching for 1 words
# -- 0 of the words in kw_list were found, out of 1 or 0%
# --  2.80 microseconds per search
# Search only includes words that appear on the site
# - Searching for 38 words
# -- 38 of the words in kw_list were found, out of 38 or 100%
# --  3.33 microseconds per search
# - Searching for 3 words
# -- 3 of the words in kw_list were found, out of 3 or 100%
# --  4.73 microseconds per search
# - Searching for 1 words
# -- 1 of the words in kw_list were found, out of 1 or 100%
# --  7.16 microseconds per search
# Depth =  1
# 598 have been stored in the crawl
# 10.7% of random words are in known words
#
#
# Data Structure: <class 'BST.BinarySearchTree'>
# Crawl and Store took 0.58 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# -- 64 of the words in kw_list were found, out of 598 or 11%
# -- 10.07 microseconds per search
# - Searching for 59 words
# -- 7 of the words in kw_list were found, out of 59 or 12%
# -- 10.11 microseconds per search
# - Searching for 5 words
# -- 0 of the words in kw_list were found, out of 5 or 0%
# -- 10.74 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# -- 598 of the words in kw_list were found, out of 598 or 100%
# --  8.70 microseconds per search
# - Searching for 59 words
# -- 59 of the words in kw_list were found, out of 59 or 100%
# --  8.60 microseconds per search
# - Searching for 5 words
# -- 5 of the words in kw_list were found, out of 5 or 100%
# --  9.01 microseconds per search
#
#
# Data Structure: <class 'splay_tree.SplayTree'>
# Crawl and Store took 0.62 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# -- 64 of the words in kw_list were found, out of 598 or 11%
# -- 14.76 microseconds per search
# - Searching for 59 words
# -- 3 of the words in kw_list were found, out of 59 or 5%
# -- 12.47 microseconds per search
# - Searching for 5 words
# -- 0 of the words in kw_list were found, out of 5 or 0%
# --  8.38 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# -- 598 of the words in kw_list were found, out of 598 or 100%
# -- 17.17 microseconds per search
# - Searching for 59 words
# -- 59 of the words in kw_list were found, out of 59 or 100%
# -- 14.47 microseconds per search
# - Searching for 5 words
# -- 5 of the words in kw_list were found, out of 5 or 100%
# --  5.39 microseconds per search
#
#
# Data Structure: <class 'AVL_tree.AVLTree'>
# Crawl and Store took 0.60 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# -- 64 of the words in kw_list were found, out of 598 or 11%
# --  8.22 microseconds per search
# - Searching for 59 words
# -- 7 of the words in kw_list were found, out of 59 or 12%
# --  8.15 microseconds per search
# - Searching for 5 words
# -- 0 of the words in kw_list were found, out of 5 or 0%
# --  9.14 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# -- 598 of the words in kw_list were found, out of 598 or 100%
# --  7.44 microseconds per search
# - Searching for 59 words
# -- 59 of the words in kw_list were found, out of 59 or 100%
# --  6.92 microseconds per search
# - Searching for 5 words
# -- 5 of the words in kw_list were found, out of 5 or 100%
# --  7.29 microseconds per search
#
#
# Data Structure: <class 'hash_table.HashQP'>
# Crawl and Store took 0.58 seconds
# Search is random from total pool of random words
# - Searching for 598 words
# -- 64 of the words in kw_list were found, out of 598 or 11%
# --  2.77 microseconds per search
# - Searching for 59 words
# -- 6 of the words in kw_list were found, out of 59 or 10%
# --  2.73 microseconds per search
# - Searching for 5 words
# -- 1 of the words in kw_list were found, out of 5 or 20%
# --  2.93 microseconds per search
# Search only includes words that appear on the site
# - Searching for 598 words
# -- 598 of the words in kw_list were found, out of 598 or 100%
# --  2.99 microseconds per search
# - Searching for 59 words
# -- 59 of the words in kw_list were found, out of 59 or 100%
# --  2.99 microseconds per search
# - Searching for 5 words
# -- 5 of the words in kw_list were found, out of 5 or 100%
# --  2.83 microseconds per search
# Depth =  2
# 3920 have been stored in the crawl
# 71.8% of random words are in known words
#
#
# Data Structure: <class 'BST.BinarySearchTree'>
# Crawl and Store took 7.11 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# -- 2814 of the words in kw_list were found, out of 3920 or 72%
# -- 12.72 microseconds per search
# - Searching for 392 words
# -- 293 of the words in kw_list were found, out of 392 or 75%
# -- 12.39 microseconds per search
# - Searching for 39 words
# -- 26 of the words in kw_list were found, out of 39 or 67%
# -- 12.29 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# -- 3920 of the words in kw_list were found, out of 3920 or 100%
# -- 12.72 microseconds per search
# - Searching for 392 words
# -- 392 of the words in kw_list were found, out of 392 or 100%
# -- 12.83 microseconds per search
# - Searching for 39 words
# -- 39 of the words in kw_list were found, out of 39 or 100%
# -- 11.43 microseconds per search
#
#
# Data Structure: <class 'splay_tree.SplayTree'>
# Crawl and Store took 6.87 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# -- 2814 of the words in kw_list were found, out of 3920 or 72%
# -- 20.90 microseconds per search
# - Searching for 392 words
# -- 296 of the words in kw_list were found, out of 392 or 76%
# -- 15.83 microseconds per search
# - Searching for 39 words
# -- 29 of the words in kw_list were found, out of 39 or 74%
# -- 10.63 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# -- 3920 of the words in kw_list were found, out of 3920 or 100%
# -- 22.50 microseconds per search
# - Searching for 392 words
# -- 392 of the words in kw_list were found, out of 392 or 100%
# -- 15.84 microseconds per search
# - Searching for 39 words
# -- 39 of the words in kw_list were found, out of 39 or 100%
# --  9.41 microseconds per search
#
#
# Data Structure: <class 'AVL_tree.AVLTree'>
# Crawl and Store took 7.14 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# -- 2814 of the words in kw_list were found, out of 3920 or 72%
# -- 10.31 microseconds per search
# - Searching for 392 words
# -- 277 of the words in kw_list were found, out of 392 or 71%
# --  9.95 microseconds per search
# - Searching for 39 words
# -- 28 of the words in kw_list were found, out of 39 or 72%
# --  9.45 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# -- 3920 of the words in kw_list were found, out of 3920 or 100%
# -- 10.51 microseconds per search
# - Searching for 392 words
# -- 392 of the words in kw_list were found, out of 392 or 100%
# --  9.34 microseconds per search
# - Searching for 39 words
# -- 39 of the words in kw_list were found, out of 39 or 100%
# --  8.90 microseconds per search
#
#
# Data Structure: <class 'hash_table.HashQP'>
# Crawl and Store took 6.76 seconds
# Search is random from total pool of random words
# - Searching for 3920 words
# -- 2814 of the words in kw_list were found, out of 3920 or 72%
# --  3.11 microseconds per search
# - Searching for 392 words
# -- 264 of the words in kw_list were found, out of 392 or 67%
# --  2.90 microseconds per search
# - Searching for 39 words
# -- 27 of the words in kw_list were found, out of 39 or 69%
# --  3.06 microseconds per search
# Search only includes words that appear on the site
# - Searching for 3920 words
# -- 3920 of the words in kw_list were found, out of 3920 or 100%
# --  4.21 microseconds per search
# - Searching for 392 words
# -- 392 of the words in kw_list were found, out of 392 or 100%
# --  2.94 microseconds per search
# - Searching for 39 words
# -- 39 of the words in kw_list were found, out of 39 or 100%
# --  2.99 microseconds per search
# Depth =  3
# 5298 have been stored in the crawl
# 97.2% of random words are in known words
#
#
# Data Structure: <class 'BST.BinarySearchTree'>
# Crawl and Store took 67.96 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# -- 5149 of the words in kw_list were found, out of 5298 or 97%
# -- 12.72 microseconds per search
# - Searching for 529 words
# -- 508 of the words in kw_list were found, out of 529 or 96%
# -- 13.15 microseconds per search
# - Searching for 52 words
# -- 51 of the words in kw_list were found, out of 52 or 98%
# -- 12.67 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# -- 5298 of the words in kw_list were found, out of 5298 or 100%
# -- 13.14 microseconds per search
# - Searching for 529 words
# -- 529 of the words in kw_list were found, out of 529 or 100%
# -- 12.25 microseconds per search
# - Searching for 52 words
# -- 52 of the words in kw_list were found, out of 52 or 100%
# -- 11.50 microseconds per search
#
#
# Data Structure: <class 'splay_tree.SplayTree'>
# Crawl and Store took 74.82 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# -- 5149 of the words in kw_list were found, out of 5298 or 97%
# -- 23.29 microseconds per search
# - Searching for 529 words
# -- 516 of the words in kw_list were found, out of 529 or 98%
# -- 17.03 microseconds per search
# - Searching for 52 words
# -- 49 of the words in kw_list were found, out of 52 or 94%
# -- 10.52 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# -- 5298 of the words in kw_list were found, out of 5298 or 100%
# -- 23.36 microseconds per search
# - Searching for 529 words
# -- 529 of the words in kw_list were found, out of 529 or 100%
# -- 16.17 microseconds per search
# - Searching for 52 words
# -- 52 of the words in kw_list were found, out of 52 or 100%
# -- 10.13 microseconds per search
#
#
# Data Structure: <class 'AVL_tree.AVLTree'>
# Crawl and Store took 68.40 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# -- 5149 of the words in kw_list were found, out of 5298 or 97%
# -- 10.52 microseconds per search
# - Searching for 529 words
# -- 517 of the words in kw_list were found, out of 529 or 98%
# -- 10.21 microseconds per search
# - Searching for 52 words
# -- 52 of the words in kw_list were found, out of 52 or 100%
# --  9.77 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# -- 5298 of the words in kw_list were found, out of 5298 or 100%
# -- 10.53 microseconds per search
# - Searching for 529 words
# -- 529 of the words in kw_list were found, out of 529 or 100%
# -- 10.09 microseconds per search
# - Searching for 52 words
# -- 52 of the words in kw_list were found, out of 52 or 100%
# --  9.99 microseconds per search
#
#
# Data Structure: <class 'hash_table.HashQP'>
# Crawl and Store took 73.56 seconds
# Search is random from total pool of random words
# - Searching for 5298 words
# -- 5149 of the words in kw_list were found, out of 5298 or 97%
# --  3.84 microseconds per search
# - Searching for 529 words
# -- 513 of the words in kw_list were found, out of 529 or 97%
# --  3.30 microseconds per search
# - Searching for 52 words
# -- 51 of the words in kw_list were found, out of 52 or 98%
# --  3.17 microseconds per search
# Search only includes words that appear on the site
# - Searching for 5298 words
# -- 5298 of the words in kw_list were found, out of 5298 or 100%
# --  3.77 microseconds per search
# - Searching for 529 words
# -- 529 of the words in kw_list were found, out of 529 or 100%
# --  3.46 microseconds per search
# - Searching for 52 words
# -- 52 of the words in kw_list were found, out of 52 or 100%
# --  3.00 microseconds per search
# 10 search trials and 1 crawl trials were conducted
#
# Process finished with exit code 0
