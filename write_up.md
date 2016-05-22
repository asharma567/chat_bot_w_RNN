### How would you evaluate your autosuggest server? If you made another version, how would you compare the two to decide which is better?

The short answer is an A/B test where the control group are users of model A and the test group users of model B. Alternatively, we could also explore the application of a Multi-Arm Bandit algorithm but lets just stick with A/B testing for simplicity's sake .

First I'd attempt to figure out the desireable performance metric we're trying to optimize from a business perspective.

**Metrics**
1. Average number of key-strokes/suggestion clicks by a customer service rep per customer.
1. Average time spent per customer.
1. Average number suggestions used.


Since the goal is to minimize typing (key-strokes) by the customer service rep lets choose metric (1). 

It's easy to assume that (2) might be the ultimate goal. This tool could potentially lead to richer and longer chats with customers leaving them with a positive impression of a customer centric company. Also, some topics might take longer than others though you could control for this, it'll increase the complexity of this test. So I felt there were better options than (2). 

As for (3), it doesn't account for the additional key-strokes the user has to type in. I believe (1) is the best option in this case since it really narrows down on the business objective of the model ###to minimize keystrokes.

**Hypothesis test**
    
    Leveraging principles of CLT we could use the Difference of Means test. After randomly sampling users from each of the cohorts and taking the average number of key-strokes/suggestion clicks from the users, we arrive to a statistically significant conclusion about which model's better.

At the end of this evaluation we should be able to say on average users of model A used less keystrokes than model B. This way we can confidently reject the notion that this result occurred by random chance.

_Note: duration of test, sample size, CI will all have to be determined before hand._


---


### One way to improve the autosuggest server is to give topic-specific suggestions. How would you design an auto-categorization server? It should take a list of messages and return a TopicId. (Assume that every conversation in the training set has a TopicId).


Assumming the list of messages represents a dialogue, there are a few approaches we can take but lets focus on these two:

1. similarity query using TFIDF -> LSI -> Similarity Matrix
1. training a classifier on the vectorized corpus.

Buildout approach (2) if (1) doesn't work well. Why? Because the classifier can use the TFIDF feature matrix built in (1).

**1)**

    First, you'll have to pre-process the text in the corpus. For a case of topic modeling, I would treat each dialogue as a document. Now that we have our documents identified in the corpus we need to normalize the text within each document i.e. removing stop words, stemming/lemmatization, dealing with typos, etc. 

    Another important factor is the way in which we tokenize of each document. We have a number of options ranging from character-grams, uni-grams, bi-grams,..., skip-grams, etc. Often times I use some combination of uni-grams, bi-grams, character-grams (if there are typos).

    Once we have parameters configured we can transform/vectorize our entire corpus into a TFIDF vector space then transform that into LSI vector space. We vectorize each new and unseen document with the same parameters and transformations as we did the corpus and compute the similarity of the resulting vector versus each document in our corpus for a prediction. Using a threshold for the similarity index we could retrieve the TopicId of the most similar document. Here's another area where various similarity metrics can be used but a good starting point is cosine similarity.

#### _If the results of this don't work well. No problem! All is not lost..._

**2)**

    We can train a classifier on the aforementioned TFIDF matrix and use the TopicId as labels. There will be a model selection process where we test classifiers ranging from Logistic Regression, SVM, naive bayes, and ensemble Gradient Boosted Trees & Random Forest. These models should be grid searched for their optimal hyper-parameters and evaluated on performance. Once we figure out which model we're happy with we can serialize the classifier & TFIDF vectorizer and wrap it into a restful api and ping it with list of chat messages as input and it would output the TopicId. 

    An obstacle we'll likely come across for this method will be on how to handle class imbalance. Some examples are as follows - under/oversampling, sample weighting, combining the minor classes, layering multiple models, etc.

_Special note, in the event that we don't have the TopicIds we could use topic modelers like NMF, LDA, LDA2VEC to figure out the number of distinct topics within the corpus of chats._


---


### How would you evaluate if your auto-categorization server is good?

You could evaluate the classifier(s) through traditional ML/statistical methods: K-fold crossvalidation, Leave One Out K-Fold validation, test/validation/train split. 

Assuming this is already properly addressed then we could inspect the usage of suggestions via A/B testing. The control group would be the usage of suggestions with the autocategorization server and test group would be without the server. Just as before we'd try to see if there's a statistically significant difference in the performance metric we've chosen: (1) denoted above. 


---


### Processing hundreds of millions of conversations for your autosuggest and auto-categorize models could take a very long time. How could you distribute the processing across multiple machines?

**Prediction**

    Distributing the model to different end points for load balancing. Using Apache Storm for streaming computation close to realtime speeds. 

**Training and Preprocessing**

    Hadoop and Spark should do the trick here. Most preprocessing could even be done using MapReduce. As for scalable modeling algorithms, MLlib and Mahout should have what we need.