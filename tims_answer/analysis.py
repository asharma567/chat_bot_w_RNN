#loads library and dictionary
import json, re
import cPickle
import operator
from flask import Flask, jsonify
from pprint import pprint

def createDictionary(wordCount = 3, filename = 'lookupDict.p'):
    # initialized file load and removes most contractions. Ideally, I'd also run a spell check, but would need a 
    # list of names + unique places, so I forgo that process.
    k = json.load(open('sample_conversations.json'))
    allIssues = k['Issues']
    messageList = {}
    lookupDict = {}
    replaceDict = {"'m":' am', "'ve":' have', "'ll":" will", "'d":" would", "'s":" is", "'re":" are", "  ":" ", "' s": " is"}

    '''
    basically what this does it 
    i) parse each chat dialogue by line (one way) 
    ii) normalize the code: lower and abreviations  
    iii) put it's in a counter dictionary

    '''

    # removes all customer texts and only takes in a lower-case version of the customer interaction, saved into a dict
    for i in allIssues:
        for msg in i['Messages']:
            if not msg['IsFromCustomer']:
                #this grabs the line
                smallMsg = re.findall(r"[\w' ]+", msg['Text'])
                #[u'Hello Werner how may I help you today']
                for sMsg in smallMsg:
                    thisMessage = sMsg.strip().lower()

                    if len(thisMessage) > 1:
                        
                        for item in replaceDict:
                            # this simply replaces the messages
                            thisMessage = thisMessage.replace(item, replaceDict[item])

                        #creates a line-by-line counter
                        if thisMessage not in messageList.keys():
                            messageList[thisMessage] = 1
                        else:
                            messageList[thisMessage] += 1


    # uses the dictionary to create a master dictionary where the lookup will happen. The idea being that
    # over time, commonly used phrases will be counted more often.
    
    for customer_service_line_key in messageList:
        length_of_line_ctr = 0
        #this actually isn't used
        checker_ctr = 0
    
        for char in customer_service_line_key:
            
            if checker_ctr < 3:
                
                # if a char is a space, increment checker_ctr
                if char == ' ': checker_ctr += 1
                
                # counts the length of the line
                length_of_line_ctr += 1

        for index in range(1, length_of_line_ctr):
            if customer_service_line_key[:index] not in lookupDict:

                lookupDict[customer_service_line_key[:index]] = {}
                lookupDict[customer_service_line_key[:index]][customer_service_line_key] = messageList[customer_service_line_key]
            
            elif customer_service_line_key not in lookupDict[customer_service_line_key[:index]]:
                lookupDict[customer_service_line_key[:index]][customer_service_line_key] = messageList[customer_service_line_key]

    # pickles the file 
    f = file(filename, 'wb')
    cPickle.dump(lookupDict, f)



def findPhrase(phrase):
    # finds the phrase by first checking how many words there are
        
    wordCount = phrase.count(' ')
    myPhrase = phrase.lower()
    
    # if less than 3 words
    if wordCount <= 2:
        try:
            thisDict = lookupDict[myPhrase]
            sortedDict = sorted(thisDict.items(), key=operator.itemgetter(1), reverse=True)[:5]
    
            return [x.capitalize().replace(' i ', ' I ') for (x,y) in sortedDict]
        except KeyError:
            return []
    
    # otherwise, picks up the dictionary assorted and only picks out relevant data
    else:
        length_of_line_ctr = 0
        checker_ctr = 0
        
        for i in myPhrase:
            if checker_ctr < 3:
                if i == ' ':
                    checker_ctr += 1
                length_of_line_ctr += 1
        
        try:
            thisDict = lookupDict[myPhrase[:length_of_line_ctr - 1]]
            miniDict = {}
            
            pprint(thisDict)

            for i in thisDict:
                if i[:len(myPhrase)] == myPhrase:
                    miniDict[i] = thisDict[i]
                    
            sortedDict = sorted(miniDict.items(), key=operator.itemgetter(1), reverse=True)[:5]
            return [x.capitalize().replace(' i ', ' I ') for (x,y) in sortedDict]
        except KeyError:
            return []

if __name__ == '__main__':
    lookupDict = cPickle.load(open('lookupDict.p'))
    print findPhrase('where the hoes at')
