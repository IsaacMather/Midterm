from LinkFisher import link_fisher, _link_fisher
from EricReed import tag_visible, words_from_html, text_harvester
from KeywordEntry import KeywordEntry


class WebStore:
    # webstore objects will have the ability to crawl websites
    # recursively and store all the text that is found. You have already
    # written most of this code.

    # Webstore will rely on your KeywordEntry class, and the link_fisher(
    # ) and text_harvester() functions that you have previously written.
    # Make sure these are at the top of your file and outside the
    # WebStore class. We will set up the crawling part of the WebStore
    # today, and most of the search functionality later.
    def __init__(self, ds):
        self._store = ds() #is this right?

        #do you remember that you can pass any object to a python method,
        # and that a class is an object? ds will represent the dataset class
        # that our WebStore class will use to store all of the information
        # it finds. That's right, we are not going to code a particular data
        # structure into our class, but we will leave it flexible to use any
        # data structure that has insert() and find() implemented. In
        # __init__() we will create an object of self._store of type ds.
        # Puzzle through this , and ask if you are not sure.


    def crawl(self, url:str, depth:0, reg_ex=""):

        #like all of this shit is in crawl and list
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

        #use link_fisher(), passing the three parameters thatt were passed
        # to crawl, to capture a list of links. Iterate through the list of
        # links and capture the text on each page. For each word found,
        # either update using the KeywordEntry add() method or create a new
        # KeywordEntry object for that word. Make sure there is only one
        # KeywordEntry object for each word, regardless of how many
        # different pages contain that word. Only store alphabetic words
        # that are four or more letters ling.
        pass

    def search(self, keyword: str):
        #Okay we said we wouldn't do search yet, but we do need to make sure
        # things are loaded correctly. This method will just be a placeholder,
        # and should return a list (not a KeywordENtry object) of all pages
        # that contain keyword.
        pass

    def search_list(self,kw_list: list):
        try:

        # THis is just a wrapper for our search method. It should iterate \
        # through kw_list, calling search() for each item in the lsit. Be
        # sure to wrap the call to search() in a try/except block as we will
        # be searching for many items that we know are not in the dataset.
        # Keep track of how many words from kw_list were found in the craled
        # pages and return a tuple (found, not found).
        pass

    def crawl_and_list(self, url, depth=0, reg_ex=''):
        word_set = set()
        for link in link_fisher(url, depth, reg_ex):
            for word in text_harvester(link):
                if len(word) < 4 or not word.isalpha():
                    continue
                word_set.add(word)
        return list(word_set)