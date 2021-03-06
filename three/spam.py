import os
from collections import Counter
from nltk.corpus import stopwords
import gensim, logging
from stemming.porter2 import stem
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.svm import SVC, NuSVC, LinearSVC
from sklearn.metrics import confusion_matrix
import re


train_dir_ham = "train_data/ham"
train_dir_spam = "train_data/spam"

ham = [os.path.join(train_dir_ham,f) for f in os.listdir(train_dir_ham)]
ham_holdout = ham[len(ham)-100:len(ham)]


spam = [os.path.join(train_dir_spam,f) for f in os.listdir(train_dir_spam)]
spam_holdout = spam[len(spam)-100:len(spam)]


emails = ham + spam
holdout = ham_holdout + spam_holdout

def build_dictionary():

    all_words = []
    for i, email in enumerate(emails):
        if i % 100 == 0:
            print i
        with open(email) as m:
            for line in m:
                words = line.split()
                for word in words:
                    word = stem(word.lower())
                all_words += words
    dictionary = Counter(all_words)
    stopWords = set(stopwords.words('english'))
    list_to_remove = dictionary.keys()
    for item in list_to_remove:
        if item.isalpha() == False:
            del dictionary[item]
        elif len(item) == 1:
            del dictionary[item]
        elif item in stopWords:
            del dictionary[item]

    dictionary = dictionary.most_common(3000)
    return dictionary

def dic_from_file():
    dicFile = open('dictionary.txt')
    asdf = dicFile.read()
    asdf = asdf[2:len(asdf)-3]
    asdf = asdf.split('), (')
    dictionary = []
    for line in asdf:
        split = line.split(', ')
        word = split[0]
        word = word[1:len(word)-1]
        count = int(split[1])
        entry = (word, count)
        dictionary.append(entry)
    return dictionary

def extract_features(dictionary, files):

    features_matrix = np.zeros((len(files),3000))
    docID = 0
    for j, file in enumerate(files):
        if j % 100 == 0:
            print j
        f = open(file)
        line = f.read()
        words = line.split()
        for word in words:
            word = stem(word.lower())
            wordID = 0
            for i,d in enumerate(dictionary):
                if d[0] == word:
                    wordID = i
                    features_matrix[docID,wordID] = words.count(word)
        docID = docID + 1
    return features_matrix

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def main():

    test_dir = 'test_data'
    files = [os.path.join(test_dir,fi) for fi in os.listdir(test_dir)]
    files.sort(key=alphanum_key)

    print files

    print len(ham)
    print len(spam)
    print len(emails)

    train_labels = np.zeros(len(emails))
    train_labels[len(ham):len(emails)] = 1

    ### build dictionary and feature matrix from scratch ###
    dictionary = build_dictionary()
    dicFile = open('dictionary.txt', 'w')
    print>>dicFile, dictionary
    dicFile.close()
    train_matrix = extract_features(dictionary, emails)
    print train_matrix
    np.savetxt('feature_matrix.txt', train_matrix, fmt='%f')


    ### load dictionary and feature matrix from file ###
    dictionary = dic_from_file()
    train_matrix = np.loadtxt('feature_matrix.txt', dtype=float)


    test_matrix = extract_features(dictionary, files)
    model3 = MultinomialNB()
    model3.fit(train_matrix,train_labels)
    result3 = model3.predict(test_matrix)
    model4 = LinearSVC()
    model4.fit(train_matrix,train_labels)
    result4 = model4.predict(test_matrix)

    outFile = open('results.csv', 'w')
    print>>outFile, "email_id,labels"
    for i, label in enumerate(result3):
        email_id = str(i+1)
        label = str(int(label))
        print >> outFile, email_id + "," + label

    outFile = open('results2.csv', 'w')
    print>>outFile, "email_id,labels"
    for i, label in enumerate(result4):
        email_id = str(i+1)
        label = str(int(label))
        print >> outFile, email_id + "," + label

main()