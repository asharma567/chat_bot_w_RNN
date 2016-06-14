from collections import Counter 
import marisa_trie
import dawg
import sys

class Lookup_Data_Structures(object):
    token_frequency_table = {}
    
    def __init__(self, corpus, create_this_struct_type='MARISA'):
        
        self.token_frequency_table = Counter(corpus)
        self.structure_name = create_this_struct_type
        
        #try to think of a better structure than this
        if create_this_struct_type == 'MARISA': 
            self.lookup_table = create_TRIE(corpus)
        elif create_this_struct_type == 'dict': 
            self.lookup_table = create_frequency_dict(corpus)
        elif create_this_struct_type == 'DAWG': 
            self.lookup_table = create_DAWG(corpus)
        else:
            raise KeyError

    def __type__: 
        return self.structure_name
    
    def __size__: 
        return sys.getsizeof(lookup_table)

    def sort_by_most_frequent(self):
        return sorted(self.token_frequency_table.items(), key=lambda x:x[1], reverse=True)
    
    def lookup(self, key_strokes):
        if self.__type__ == 'dict':
            matches = self.lookup_table[key_strokes].items()
        else:
            autocompleted_matches = self.lookup_table.keys(key_strokes)
            matches = [(suggestion, self.token_frequency_table[suggestion]) for suggestion in autocompleted_matches]
        return matches

    def create_TRIE(self, corpus):
        '''
        I: corpus of documents (text)
        O: TRIE structure made for prefix lookup, counter dictionary
        '''
        return marisa_trie.Trie(corpus)

    def create_DAWG(self, corpus):
        '''
        I: corpus of documents (text)
        O: DAWG structure made for prefix lookup, counter dictionary
        '''
        return dawg.CompletionDAWG(corpus)

    def create_token_frequency_table(self, corpus):
        return Counter(corpus)

    def create_frequency_dict(self, corpus):
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
        
        key_stroke_lookup_table = {}

        for customer_service_line_key in self.token_frequency_table.keys():

            number_of_chars_in_ngram = find_num_chars_in_n_gram(customer_service_line_key, 3)
            
            # iteratively updates a dictionary
            key_stroke_lookup_table = {}

            for index in range(1, number_of_chars_in_ngram + 1):
                key_stroke_gram = customer_service_line_key[:index]
                count_of_this_particular_line = self.token_frequency_table[customer_service_line_key]
                
                if key_stroke_gram not in key_stroke_lookup_table:
                    
                    key_stroke_lookup_table[key_stroke_gram] = {}
                    key_stroke_lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line 
                
                # if the customer service line not in the key_stroke_lookup_table
                elif customer_service_line_key not in key_stroke_lookup_table[key_stroke_gram]:
                    key_stroke_lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line

        return key_stroke_lookup_table

    def dump_to_pickle(self):
        '''
        pythonically serializes lookup table

        consider using internal write methods
        '''
        
        cPickle.dump(self.lookup_table, open('lookup_table.pkl','wb'))
        cPickle.dump(self.token_frequency_table, open('token_frequency_table.pkl','wb'))
        
        return None
    
    def load_from_pickle(self, filename_prefix_lookup='lookup_table.pkl', filename_line='token_frequency_table.pkl'):
        '''
        loads pickled frequency table
        consider using internal write methods
        '''

        print 'loading: ', filename_prefix_lookup, '...',
        self.lookup_table = cPickle.load(open(filename_prefix_lookup,'rb'))
        print 'loading: ', filename_line, '...',
        self.token_frequency_table = cPickle.load(open(filename_line,'rb'))
        print 'loaded.'
        return None


    