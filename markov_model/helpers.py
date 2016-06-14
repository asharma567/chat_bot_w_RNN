import re
from concurrent.futures import ThreadPoolExecutor
import marisa_trie
from collections import Counter
import nltk.data
import spell_checker


def create_key_stroke_to_cust_line_table(customer_service_line_key, 
                                         number_of_chars_in_ngram, 
                                         corpus_ctr_dict, 
                                         lookup_table={}
                                         ):
    '''
    It walks through the n-gram string character-by-character and creates a dictionary 
    of all the possible lines this sequence of keystrokes could be leading to
    e.g.

        g {u'great was my pleasure helping you': 1}
        gr {u'great was my pleasure helping you': 1}
        ...
        great was my {u'great was my pleasure helping you': 1}

    I: string written by the customer service rep, number of characters (int), frequency distribution dictionary
    O: master lookup of table (dictionary)
    '''
    
    
    #change to key_stroke_sequence
    for index in range(1, number_of_chars_in_ngram + 1):
        key_stroke_gram = customer_service_line_key[:index]
        count_of_this_particular_line = corpus_ctr_dict[customer_service_line_key]
        
        if key_stroke_gram not in lookup_table:
            
            lookup_table[key_stroke_gram] = {}
            lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line 
        
        # if the customer service line not in the lookup_table
        elif customer_service_line_key not in lookup_table[key_stroke_gram]:
            lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line
    
    return lookup_table


def sort_by_most_frequent(ctr_dict):
    return sorted(ctr_dict.items(), key=lambda x:x[1], reverse=True)

def tokenize_by_sentence(corpus):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    return [tokenized_line for line in corpus \
                for tokenized_line in sent_detector.tokenize(line.strip())]


def find_num_chars_in_n_gram(target_str, number_of_grams):
    '''
    calculates the number of characters of a 
    the beginning ngram
    
    I: string, ngram size (int)
    O: length (int)
    '''
    
    return len(' '.join(target_str.split(' ')[:number_of_grams])) 

def format_suggestions_properly(list_of_strs):
    '''
    I: list of string
    O: properly formatted list of strings
    
    to dos
    ------
    * grammar corrections for punctuations
    '''
    output = []
    
    for str_ in list_of_strs:
        str_ = str_.capitalize().replace(' i ', ' I ')

            
        #need to think about how to add grammar
        output.append(str_)
    return output

def create_TRIE(corpus):
    '''
    I: corpus of documents (text)
    O: TRIE structure made for prefix lookup, counter dictionary
    '''
        
    return marisa_trie.Trie(corpus), Counter(corpus)


def retrieve_suggestions(key_strokes, look_up_table, top_x_lines):
    '''
    This adds an O(nlogn) time complexity to our prediction method. 
    we could avoid this by just pickling the sorted dict before hand.
    '''
    try:
        autocompleted_suggestions = prefix_lookup.keys(key_strokes)
        freq_suggestions = [(suggestion, frequency_table[suggestion]) for suggestion in autocompleted_suggestions]
        suggestions = sorted(freq_suggestions, key=lambda x:x[1], reverse=True)[:top_x_lines]
        return [tuple_[0] for tuple_ in suggestions]
    except TypeError:
        try:
            sub_dict_of_suggestions = look_up_table[key_strokes]

            #grabs the top X number of lines sorted by count (most popular)
            suggestions = sorted(sub_dict_of_suggestions.items(), key=lambda x:x[1], reverse=True)[:top_x_lines]

            return [tuple_[0] for tuple_ in suggestions]
        except KeyError:
            return None

def retrieve_suggestions_TRIE(key_strokes, prefix_lookup, frequency_table, top_x_lines):
    '''
    This adds an O(nlogn) time complexity to our prediction method. 
    we could avoid this by just pickling the sorted dict before hand.
    '''
    autocompleted_suggestions = prefix_lookup.keys(key_strokes)
    freq_suggestions = [(suggestion, frequency_table[suggestion]) for suggestion in autocompleted_suggestions]
    suggestions = sorted(freq_suggestions, key=lambda x:x[1], reverse=True)[:top_x_lines]
    return [tuple_[0] for tuple_ in suggestions]


def add_question_mark_or_period_to_sentence(target_str):
    '''
    Just adds a period or a question mark to the end of the string. 
    Hacky short term fix for the sentence type detection. 

    I: string
    O: formatted string
    '''
    
    if '?' in target_str: 
        return target_str
    
    begining_words_of_questions = {
        'what',
        'when',
        'will',
        'why',       
        'is',
        'have',
        'did',
        'will',
        'can',
        'do',
        'how',
        'could'
    }

    starting_word = target_str.split(' ', 1)[0]
    if starting_word in begining_words_of_questions:
        return target_str + '?'
    else:
        if target_str[-1] != '.': return target_str + '.'
    return target_str


def multithread_map(fn, work_list, num_workers=50):
    '''
    spawns a threadpool and assigns num_workers to some 
    list, array, or any other container. Motivation behind 
    this was for functions that involve scraping.
    '''

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        return list(executor.map(fn, work_list))

ABREVIATIONS_DICT = {
    "'m":' am',
    "'ve":' have',
    "'ll":" will",
    "'d":" would",
    "'s":" is",
    "'re":" are",
    "  ":" ",
    "' s": " is",
}

def multiple_replace(text, adict=ABREVIATIONS_DICT):
    '''
    Does a multiple find/replace
    '''
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)


def custome_refine(target_str):
    '''
    Just a temporary hack of function
    '''
    words_to_replace = {
    'welcomed': 'welcome'
    }

    return multiple_replace(target_str, words_to_replace)

def token_level_process(line):
    
    #expanding the abreviations
    line = multiple_replace(line)
    
    #spell check *note this function takes quite a bit of time
    line = correct_spelling(line)
    
    #further refinement 
    line = add_question_mark_or_period_to_sentence(line)
    
    line = custome_refine(line)
    
    return line
        

    
def correct_spelling(line):
    return ' '.join([spell_checker.correct(word) for word in line.strip().split()])
