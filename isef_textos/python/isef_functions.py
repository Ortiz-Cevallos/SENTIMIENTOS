# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:09:09 2020

@author: q31487
"""
import pandas as pd
from datetime import datetime
import numpy as np
try:
    import pyprind
    PYPRIND = True
except:
    from tqdm import tqdm
    PYPRIND = False

import os, sys
def get_application_path():
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path


def get_increment(match_name, negate):
    positive, negative = 0, 0
    if match_name == "*":
        positive = 0
        negative = 0
    elif negate:
        if match_name=="-":
            positive = 0 # double negations are neutral
        else:
            negative = 1
    # No modifier
    else:
        if match_name=="-":
            negative = 1
        else:
            positive = 1
    return positive, negative

def get_slope(df, index, values):
    slope = pd.Series(np.gradient(tmp_[values]), tmp_[index], name='slope')

    #df = pd.concat([tmp_.rename('values'), slope], axis=1)
    return slope


def count_words(nlp, text_list, sent_dict, file_pattern, bar, matcher, accented):
    rand_words = pd.DataFrame( columns=["positive", "negative", "score"])
    df_sent = pd.DataFrame(columns=["filename", "sentence", "positive", "negative", "words","negation"])
    df_index = pd.DataFrame(columns=["filename","date", "i", "score"])
    
    # the dictionary contains the default tone plus the variations
    rand_words_len = len(sent_dict[list(sent_dict.keys())[0]]['sentiment'])-1
    index_range = []
    tuple_list = []
    # Iterate through each FSR
    for row in text_list:
        (filename, body) = row
        if PYPRIND:
            bar.update(item_id = filename)
        else:
            bar.update()
            bar.set_postfix_str(filename, refresh=True)
        positive_values = [0] * (rand_words_len+1)
        negative_values = [0] * (rand_words_len+1)
        body = body.lower()
        if not accented:
            # replace diacritical marked vowels
            a,b = 'áéíóúü','aeiouu'
            trans = str.maketrans(a,b)
            body = body.translate(trans)
        doc = nlp(body)
        for sent in doc.sents:
            negative = 0
            positive = 0
            subdoc = nlp.make_doc(sent.text)
            matches = matcher(subdoc)
            negation = []
            words = {"+":[], "-":[], "*":[]}
            for match_id, start, end in matches:
                item1 = subdoc[start-1:start].text
                item2 = subdoc[start-2:start-1].text
                item3 = subdoc[start-3:start-2].text
                # add the matched word to the list of words
                matched_word = subdoc[start:end].text
                
                # retrieve the default sentiment of the word
                match_name = sent_dict[matched_word]['sentiment'][0]
                words[match_name].append(matched_word)
                # Check for negation of the term
                if any(x in [item1, item2, item3] for x in ["menos","no","nunca", "sin", "pérdida", "disminución"]): 
                    negation.append(subdoc[start:end].text)
                    negate = True
                else:
                    negate = False
                    
                
                p_inc, n_inc = get_increment(match_name, negate)
                positive += p_inc
                negative += n_inc
                
                # iterate through the different scenarios 
                for ind, sentiment in enumerate(sent_dict[matched_word]['sentiment'][0:]):
                    p_inc, n_inc = get_increment(sentiment, negate)
                    positive_values[ind] += p_inc
                    negative_values[ind] += n_inc
                        
            # add sentence at the end of the dataframe
            tuple = [[filename,subdoc.text, positive, negative, ", ".join(words["+"]),", ".join(words["-"]), ", ".join(words["*"]), ", ".join(negation)]]
            tuple_list += tuple
        # Calculate score for each combination of words
        rand_words["negative"] = negative_values
        rand_words["positive"] = positive_values
        rand_words["score"] = (rand_words["negative"] - rand_words["positive"])/(rand_words["positive"] + rand_words["negative"])
        # For each FSR calculate max and min score of the different word combinations
        index_range.append([filename,rand_words["score"].max(), rand_words["score"].min()])
        rand_words["filename"] = filename
        rand_words["i"]=rand_words.index
        rand_words["date"]=rand_words['filename'].apply(lambda x: datetime.strptime(x,file_pattern))
        # Transform dates to integer of days since 2002-11-01 divided by 100 to use for the gradient
        df_index = pd.concat([df_index,rand_words[["filename","date", "i", "score"]]])
    df_sent = pd.DataFrame(tuple_list, columns=["filename", "sentence", "positive", "negative", "pos_words", "neg_words", "neu_words","negation"])        
    return df_sent, index_range, df_index