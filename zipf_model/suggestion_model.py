import json
import nltk.data
import spell_checker
from collections import Counter
import cPickle
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
    predict
    read_in_corpus
    create_frequency_dict
    find_suggestions
    preprocess
    load_from_pickle
    dump_to_pickle
    print_corpus
    

    to dos:
    -------
    * unit tests
        - enumerate possible inputs that will break find_suggestions
        - try to break the rest of the functions
    
    PREPROCESS
    * fix grammar
    * remove names
    * research how to deal with punctuation and 
    * removing infrequent terms 
    * multithread the spellchecker
    * iterate through with a string fuzzy matching algo to dedupe typos

    FIND_SUGGESTIONS
    * threshold the number suggestions by the frequency of suggested term
    '''
    
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
        
        #make counter dict 
        self.key_stroke_lookup_table = self.create_frequency_dict(self.preprocessed_corpus)
    
    def print_corpus(self, corpus, dump_to_txt=False, counter_table=False):
        '''
        This is a debugging tool used to view the distribution of documents 
        (customer service strings) within the corpus.
        
        I: corpus
        O: None
        '''
        print type(corpus)
        print corpus[:5]
        if counter_table:
            sorted_line_counts = sorted(Counter(corpus).items(), key=lambda x:x[1], reverse=True)
            output = '\n'.join(str(tuple_[1]) + ' | ' + tuple_[0] for tuple_ in sorted_line_counts)
        else:
            output = '\n'.join(corpus)
        if dump_to_txt:
            
            with open('corpus.txt','wb') as f:
                f.write(output)
        else:
            print '\n'.join(output)
        return None

    def create_frequency_dict(self, corpus):
        '''
        I: corpus of documents (text)
        O: frequency table (dictionary where keys are documents and values are counts)
        '''
        
        key_stroke_lookup_table = {}

        #change: line_frequency_table
        corpus_ctr_dict = Counter(corpus)

        for customer_service_line_key in corpus_ctr_dict.keys():

            number_of_chars_in_ngram = find_num_chars_in_n_gram(customer_service_line_key, 3)
            key_stroke_lookup_table = create_key_stroke_to_cust_line_table(
                                            customer_service_line_key,
                                            number_of_chars_in_ngram,
                                            corpus_ctr_dict,
                                            key_stroke_lookup_table
                                            )

        return key_stroke_lookup_table


    
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

    def find_suggestions(self, key_stroke_sequence_str, top_x_lines=5):
        '''
        I: key stroke sequence e.g 'what th' (string), max number of suggestions (int) 
        O: suggestions that attempt to accurately complete the key stroke sequence (list of strings)
        '''

        look_this_up = key_stroke_sequence_str.lower()
        number_of_words = len(key_stroke_sequence_str.split())

        if number_of_words <= 2:

            #pull up the most frequently occuring line
            most_frequent_lines = retrieve_suggestions(look_this_up, self.key_stroke_lookup_table, top_x_lines)

        else:   

            #truncate the target sequence of key strokes to the first tri-gram
            #perhaps we could have something similar in our lookup table
            len_of_key_strokes = find_num_chars_in_n_gram(look_this_up, 3)
            truncated_key_strokes = look_this_up[:len_of_key_strokes - 1]
            most_frequent_lines = retrieve_suggestions(truncated_key_strokes, self.key_stroke_lookup_table, top_x_lines)

        return most_frequent_lines

    
    def preprocess(self, corpus):
        '''
        This iterates through the corpus line by line tokenizing, 
        spellchecking, normalizing abbreviations, etc.

        It's debatable how you want to tokenize, I chose to do it by sentence
        but it could be done with regex like so "[\w' ]+" which would give you 
        smaller phrases.
        
        I: list of text strings
        O: preprocessed list of text strings
        '''
        
        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        
        #lowercase and tokenize by sentence
        corpus_formatted = [tokenized_line for line in corpus \
                            for tokenized_line in sent_detector.tokenize(line.strip().lower())]

        
        #expanding the abreviations
        corpus_formatted_expanded = [multiple_replace(line) for line in corpus_formatted]

        #spell check
        #note this function takes quite a bit of time
        corpus_formatted_expanded_correct = [' '.join([spell_checker.correct(word) for word in line.strip().split()]) 
                                             for line in corpus_formatted_expanded]
        
        
        return corpus_formatted_expanded_correct

    def dump_to_pickle(self):
        '''
        pythonically serializes lookup table
        '''
        
        cPickle.dump(self.key_stroke_lookup_table, open('key_stroke_lookup_table.pkl','wb'))
        return None
    
    def load_from_pickle(self, filename='key_stroke_lookup_table.pkl'):
        '''
        loads pickled frequency table
        '''

        print 'loading: ', filename, '...',
        self.key_stroke_lookup_table = cPickle.load(open(filename,'rb'))
        print 'loaded.'

if __name__ == '__main__':

    #stub code just to test out the class
    model = Suggestion_Generator()
    model.train('sample_conversations.json')
    model.dump_to_pickle()
    model.print_corpus(model.preprocessed_corpus, True, True)
    print model.find_suggestions('what')