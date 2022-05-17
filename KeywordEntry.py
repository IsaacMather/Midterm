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
