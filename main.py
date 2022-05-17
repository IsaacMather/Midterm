import timeit
import random
from random_words import RandomWords
from BST import BinarySearchTree
from hash_table import HashQP
from splay_tree import SplayTree
from AVL_tree import AVLTree
from WebStore import WebStore



def test_code():
    rw = RandomWords()
    num_random_words = 5449
    search_trials = 10
    crawl_trials = 1
    structures = [BinarySearchTree, SplayTree, AVLTree, HashQP]
    for depth in range(4):
        print("Depth = ", depth)
        stores = [WebStore(ds) for ds in structures]
        known_words = stores[0].crawl_and_list("http://compsci.mrreed.com", depth)
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
        print(f"{known_count/len(random_words)*100:.1f}% of random words "
              f"are in known words")
        for i, store in enumerate(stores):
            print("\n\nData Structure:", structures[i])
            time_s = timeit.timeit(f'store.crawl("http://compsci.mrreed.com", depth)',
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
                    total_time_us = timeit.timeit('store.search_list(search_list)',
                                setup="from __main__ import store, search_list",
                                number=search_trials)
                    time_us = total_time_us / search_trials / list_len * (10 ** 6)
                    found, not_found = store.search_list(search_list)
                    print(f"-- {found} of the words in kw_list were found, out of "
                          f"{found + not_found} or "
                          f"{found / (not_found + found) * 100:.0f}%")
                    print(f"-- {time_us:5.2f} microseconds per search")
    print(f"{search_trials} search trials and "
          f"{crawl_trials} crawl trials were conducted")


# Press the green button in the gutter to run the script.
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
