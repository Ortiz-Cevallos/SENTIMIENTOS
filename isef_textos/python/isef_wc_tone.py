import pandas as pd

def getList_pos_neg_words(df_filt, file_str):

    """ Get the words with sentiment for selected filename

        df_filt: is dataframe with final output for each text file composed by 
        sentences with sentiment, positive words, negative words, and negations. 

        file_str: iterates along the texts in the df_filt. 
        Example: file_str = '20200505.txt'
    """

    df_report = df_filt.loc[df_filt.loc[:,'filename']== file_str]

    # choose positive
    is_word   = df_report.loc[:,'pos_words'] != str()
    df_nube_pos = df_report.loc[is_word, ['pos_words', 'negation'] ]
    # choose negative
    is_word   = df_report.loc[:,'neg_words'] != str()
    df_nube_neg = df_report.loc[is_word, ['neg_words', 'negation'] ]

    # Series To lists of positive words and negative ones
    pd.set_option("display.max_colwidth", 10000) # needed to solve the col_width bug: DataFrame.to_string truncates long strings #9784
    list_pos = df_nube_pos['pos_words'].to_string(index=False).replace('\n',',').replace(' ' , '').split(',')
    list_neg = df_nube_neg['neg_words'].to_string(index=False).replace('\n',',').replace(' ' , '').split(',')

    # For negative words, remove negations from negative list
    for ind in df_nube_neg.index:
        negation_aux_list = df_nube_neg['negation'][ind].replace(' ' , '').split(',')
        aux_list = df_nube_neg['neg_words'][ind].replace(' ' , '').split(',')
        if df_nube_neg['negation'][ind] != str():
            for word in negation_aux_list:
                if word in aux_list:
                    list_neg.remove(word)

    # For positive words, add negations to negative words list and remove from positive list
    for ind in df_nube_pos.index:
        negation_aux_list = df_nube_pos['negation'][ind].replace(' ' , '').split(',')
        aux_list = df_nube_pos['pos_words'][ind].replace(' ' , '').split(',')
        if df_nube_pos['negation'][ind] != str():
            for word in negation_aux_list:
                if word in aux_list:
                    list_neg.append(word)
                    list_pos.remove(word)

    return list_pos, list_neg


# Some aux functions for word cloud
class GroupedColorFunc(object):
    """Create a color function object which assigns colors
       to certain words based on a color to words mapping

       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.
    """
    def __init__(self, color_to_words):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word)