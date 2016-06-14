import json
from data_structures import Lookup_Data_Structures
# do this line by line
from helpers import *

class Suggestion_Generator(object):
    '''
    This class builds a retrieval based chatbot 
    and it's based off a frequency of n-grams in 
    a target corpus of text. It uses the inverse of 
    zipf's law to predict sentences by each key 
    stroke.

    Methods
    --------
    train
    read_in_corpus
    find_suggestions_given_input
    preprocess
    print_corpus
    

    to dos:
    -------
    * unit tests
        - enumerate possible inputs that will break find_suggestions_given_input
        - try to break the rest of the functions
    * dedupe corpus of customer service rep lines
        * use LSH

    PREPROCESS
    * fix grammar
    * remove names
    * research how to deal with punctuation and 
    * removing infrequent terms 
    * multithread the spellchecker
    * iterate through with a string fuzzy matching algo to dedupe typos


    FIND_SUGGESTIONS_given_input
    * threshold the number suggestions by the frequency of suggested term
    * decrease the time complexity of this function
    '''
    
    def __init__(self):
        pass


    def train(self, target_corpus_filename, filename_for_storage='n_gram_frequencies_dict.pkl'):
        '''
        This builds the lookup table from raw text in the JSON file.

        I: json file with chats e.g. 'sample_conversations.json'
        O: None
        '''
        
        #read
        self.raw_corpus = self.read_in_corpus(target_corpus_filename)

        #preprocess
        self.preprocessed_corpus = self.preprocess(self.raw_corpus)
        
        #make counter dict and prefix lookup
        self.data_store = Lookup_Data_Structures(corpus=self.preprocessed_corpus)

    
    def print_corpus(self, corpus, dump_to_txt=False, counter_table=False):
        '''
        This is a debugging tool used to view the distribution of documents 
        (customer service strings) within the corpus.
        
        I: corpus
        O: None
        '''
        
        if counter_table:
            sorted_line_counts = sort_by_most_frequent(data_store.token_frequency_table.items())
            output = '\n'.join(str(tuple_[1]) + ' | ' + tuple_[0] for tuple_ in sorted_line_counts)
        else:
            output = '\n'.join(corpus)
        if dump_to_txt:
            
            with open('corpus.txt','wb') as f:
                f.write(output)
        else:
            print '\n'.join(output)
        return None



    def read_in_corpus(self, target_corpus_filename):
        '''
        reads a json file of chats and strips on the customer service lines 
        from the chats.

        alternative options to read-in the json would've been pandas 
        but that would be very unassuming to size of the file.

        I: json file name
        O: list of customer service lines
        '''

        corpus_json = json.load(open(target_corpus_filename))
        Issues_json = corpus_json['Issues']
        all_customer_service_lines = []

        for issue_dialogue in Issues_json:
            
            customer_service_lines = [message['Text'] for message in issue_dialogue['Messages'] \
             if not message['IsFromCustomer']]

            all_customer_service_lines.extend(customer_service_lines)

        return all_customer_service_lines

    def find_suggestions_given_input(self, key_stroke_sequence_str, top_x_lines=5):
        '''
        I: key stroke sequence e.g 'what th' (string), max number of suggestions (int) 
        O: suggestions that attempt to accurately complete the key stroke sequence (list of strings)
        '''

        look_this_up = key_stroke_sequence_str.lower()
        number_of_words = len(key_stroke_sequence_str.split())

        
        if number_of_words < 2:

            #pull up the most frequently occuring line
            most_frequent_lines = self.retrieve_suggestions(look_this_up, top_x_lines)

        else:   

            #truncate the target sequence of key strokes to the first tri-gram
            #perhaps we could have something similar in our lookup table
            len_of_key_strokes = find_num_chars_in_n_gram(look_this_up, 3)
            truncated_key_strokes = look_this_up[:len_of_key_strokes - 1]
            
            most_frequent_lines = self.retrieve_suggestions(truncated_key_strokes, top_x_lines)

        return format_suggestions_properly(most_frequent_lines)
    

    def retrieve_suggestions(self, key_strokes, top_x_lines):
        '''
        This adds an O(nlogn) time complexity to our prediction method. 
        we could avoid this by just pickling the sorted dict before hand.
        '''
        
        zipfian_distributed_suggestions = sort_by_most_frequent(self.data_store.lookup(key_strokes))
        
        #peeling off the counts
        return [tuple_[0] for tuple_ in  zipfian_distributed_suggestions[:top_x_lines]]
        

    
    def preprocess(self, corpus):
        '''
        This iterates through the corpus line by line tokenizing, 
        spellchecking, normalizing abbreviations, etc.

        It's debatable how you want to tokenize, I chose to do it by sentence
        but it could be done with regex like so "[\w' ]+" which would give you 
        smaller phrases.
        
        I: list of text strings
        O: preprocessed list of text strings

        Should this be it's own class?
        '''
        
        #tokenize by sentence
        corpus_formatted = tokenize_by_sentence(corpus)
        
        return map(token_level_process, corpus_formatted)

        

if __name__ == '__main__':

    #stub code just to test out the class
    model = Suggestion_Generator()
    model.train('sample_conversations.json')
    model.dump_to_pickle()
    model.print_corpus(model.preprocessed_corpus, True, True)
    
    #this takes a substantial amount of clocktime
    model.load_from_pickle()
    print model.find_suggestions_given_input(u'what')