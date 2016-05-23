import re
from concurrent.futures import ThreadPoolExecutor


def create_key_stroke_to_cust_line_table(customer_service_line_key, 
                                         number_of_chars_in_ngram, 
                                         corpus_ctr_dict, master_lookup={}):
    '''
    what this does is it walks through the n gram string character-by-character and creates a dictionary 
    of all the possible lines this sequence of keystrokes could be leading to
    e.g.

        g {u'great was my pleasure helping you': 1}
        gr {u'great was my pleasure helping you': 1}
        ...
        great was my {u'great was my pleasure helping you': 1}
    '''
    
    
    #change to key_stroke_sequence
    for index in range(1, number_of_chars_in_ngram + 1):
        key_stroke_gram = customer_service_line_key[:index]
        count_of_this_particular_line = corpus_ctr_dict[customer_service_line_key]
        
        if key_stroke_gram not in master_lookup:
            
            master_lookup[key_stroke_gram] = {}
            master_lookup[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line 
        
        # if the customer service line not in the master_lookup
        elif customer_service_line_key not in master_lookup[key_stroke_gram]:
            master_lookup[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line
    
    return master_lookup

def find_num_chars_in_n_gram(line, number_of_grams):
    '''
    calculates the number of characters of a 
    the beginning ngram in a string
    
    I: string, ngram size (int)
    O: length (int)
    '''
    return len(' '.join(line.split(' ')[:number_of_grams])) 

def format_suggestions_properly(list_of):
    '''
    I:list of string
    O:properly formatted list of strings
    
    to dos
    ------
    * grammar corrections for punctuations
    '''
    output = []
    for str_ in list_of:
        str_ = str_.capitalize()
        str_ = str_.replace(' i ', ' I ')
        
        #need to think about how to add grammar
        str_
        output.append(str_)
    return output

def retrieve_suggestions(key_strokes, look_up_table, top_x_lines):
    try:
        sub_dict_of_suggestions = look_up_table[key_strokes]

        #grabs the top X number of lines sorted by count (most popular)
        suggestions = sorted(sub_dict_of_suggestions.items(), key=lambda x:x[1], reverse=True)[:top_x_lines]

        return [tuple_[0] for tuple_ in suggestions]
    except KeyError:
        return None

def add_question_mark_or_period_to_sentence(line):
    if '?' in line: return line
    
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

    starting_word = line.split(' ', 1)[0]
    if starting_word in begining_words_of_questions:
        return line + '?'
    else:
        if line[-1] != '.': return line + '.'
    return line


def abreviation_expander(target_str):
    
    # can add to this list
    abreviations_dict = {
        "'m":' am',
        "'ve":' have',
        "'ll":" will",
        "'d":" would",
        "'s":" is",
        "'re":" are",
        "  ":" ",
        "' s": " is",
    }
    
    for abreviated_form, full_form in abreviations_dict.iteritems():
        target_str.replace(abreviated_form, full_form)
    return target_str

def multithread_map(fn, work_list, num_workers=50):
    '''
    spawns a threadpool and assigns num_workers to some 
    list, array, or any other container. Motivation behind 
    this was for functions that involve scraping.
    '''

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        return list(executor.map(fn, work_list))

def multiple_replace(text, adict):
    rx = re.compile('|'.join(map(re.escape, adict)))
    def one_xlat(match):
        return adict[match.group(0)]
    return rx.sub(one_xlat, text)
