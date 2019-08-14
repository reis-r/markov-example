from functools import reduce, partial
from itertools import count
from random import choice
from typing import Callable, List, Iterable, Tuple, Any

# Some auxiliary functions, nothing to see here
def compose(*functions: Callable) -> Callable:
    '''Makes function composition more readable'''
    return reduce(lambda g, f: lambda x: f(g(x)), functions, lambda x: x)


def piped(obj: Any, *functions: Callable) -> Any:
    '''Applies some object into a function composition'''
    return compose(*functions)(obj)


# The real program starts here
def books_file(file_name: str) -> str:
    '''Open the books file and return it on a string'''
    return open(file_name, 'r').read()


def string_cleaner(string: str) -> str:
    '''Main function for cleaning the books string'''
    return string.replace('"', '"').replace(".", " <EOS> ")


def split(string: str) -> List[str]:
    '''Split the string into a list of words'''
    return string.split()


def build_word_sequence(wordlist: Tuple[str]) -> Iterable:
    '''Builds a (word, index) tuple'''
    return zip(wordlist, count())


# Defines a type alias for a node in the word collection
WordListNode = Tuple[str, int]


def node_word(node: WordListNode) -> str:
    '''Gets a word inside a WordListNode'''
    return node[0]


def node_index(node: WordListNode) -> int:
    '''Gets index of a word inside a WordListNode'''
    return node[1]


def next_node_index(node: WordListNode) -> int:
    return node_index(node) + 1


def node_by_index(nodes: Tuple[WordListNode], idx: int) -> WordListNode:
    '''Gets a word based on its index on a collection of WordListNode'''
    end_of_sentence = ("<EOS>", -1)
    if idx is -1:
        return end_of_sentence
    else:
        return reduce(
            lambda prev, node: node if node_index(node) == idx else prev,
            nodes,
            end_of_sentence
        )


def generate_chain(key: str, words: Tuple[WordListNode]) -> Tuple[str, ...]:
    '''Creates "the chain"'''
    def next_word(words: Tuple[WordListNode], word: str) -> str:
        '''Searches for the index of the next element of every occurrence of word'''
        return piped(
            words,
            # get all occurrences
            partial(filter, lambda node: node_word(node) == word),
            # get all possible outcomes
            partial(map, next_node_index),
            # make it a tuple
            tuple,
            # choose the next state
            lambda e: choice(e) if e else -1,
            # get the chosen node
            partial(node_by_index, words),
            # get the word
            node_word
        )

    def chain_helper(current_key: str, chain: Tuple[str, ...]) -> Tuple[str, ...]:
        '''Function to help the iteration'''
        if current_key == '<EOS>':
            return chain
        else:
            return chain_helper(
                next_word(words, current_key),
                chain + (current_key,)
            )

    return chain_helper(key, tuple())


def choose_key(options: Tuple[str, ...] = ("A", "The")) -> str:
    '''Choses a key from different options'''
    # If something goes wrong, defaults to "A"
    return choice(options) if options else "A"


def generate_reply(file_name, text: str) -> str:
    '''Function that will put everything together'''
    key = choose_key(text.split())
    return piped(
        # Open the file with the words
        books_file(file_name),
        # Clear the file
        string_cleaner,
        # Separate the words
        split,
        # Creates the WordListNodes
        build_word_sequence,
        # Consolidate everything into a Tuple
        tuple,
        # Generate the chain
        partial(generate_chain, key),
        # Generate a string from the given chain
        ' '.join
    )


text_file = "books.txt"
initial_key = piped(books_file(text_file), string_cleaner)
print(generate_reply(text_file, initial_key))
