from collections import Counter 
import marisa_trie
import dawg

class Lookup_Data_Structures(object):
    line_frequency_table = {}
    
    def __init__(self, corpus, struct_type='MARISA'):
        
        self.line_frequency_table = Counter(corpus)
        
        #try to think of a better structure than this
        if struct_type == 'MARISA': 
            self.lookup_table = create_TRIE(corpus)
        elif struct_type == 'dict': 
            self.lookup_table = create_frequency_dict(corpus)
        elif struct_type == 'DAWG': 
            self.lookup_table = create_DAWG(corpus)
        else:
            raise KeyError

    def __type__: pass
    def __size__: pass

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

    def create_line_frequency_table(self, corpus):
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

        for customer_service_line_key in self.line_frequency_table.keys():

            number_of_chars_in_ngram = find_num_chars_in_n_gram(customer_service_line_key, 3)
            
            # iteratively updates a dictionary
            key_stroke_lookup_table = {}

            for index in range(1, number_of_chars_in_ngram + 1):
                key_stroke_gram = customer_service_line_key[:index]
                count_of_this_particular_line = self.line_frequency_table[customer_service_line_key]
                
                if key_stroke_gram not in key_stroke_lookup_table:
                    
                    key_stroke_lookup_table[key_stroke_gram] = {}
                    key_stroke_lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line 
                
                # if the customer service line not in the key_stroke_lookup_table
                elif customer_service_line_key not in key_stroke_lookup_table[key_stroke_gram]:
                    key_stroke_lookup_table[key_stroke_gram][customer_service_line_key] = count_of_this_particular_line

        return key_stroke_lookup_table

    