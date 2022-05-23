from LinkFisher import link_fisher, _link_fisher
from EricReed import tag_visible, words_from_html, text_harvester
from KeywordEntry import KeywordEntry


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
        return keyword_object.sites()


    def search_list(self,kw_list: list):
        found = 0
        not_found = 0

        for keyword in kw_list:
            try:
                if self.search(keyword):
                    found += 1
            except:
                not_found += 1

        return (found, not_found)


    def crawl_and_list(self, url, depth=0, reg_ex=''):
        word_set = set()
        for link in link_fisher(url, depth, reg_ex):
            for word in text_harvester(link):
                if len(word) < 4 or not word.isalpha():
                    continue
                word_set.add(word)
        return list(word_set)