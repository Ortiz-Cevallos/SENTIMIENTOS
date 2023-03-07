# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 15:57:44 2020

@author: q31487
"""
RANDOM = False
version= "0.4"
WORDCLOUD = True
import sys
# sys.argv.append("BCCH_BdE_dict_orig.xlsx")
# ******
n_cases = 1000
# ******
print("Analizador de sentimiento de la estabilidad financiera versión "+ version)
 
import os
import re
import sys
from datetime import datetime
from isef_functions import count_words, get_application_path
import pandas as pd
import random
import spacy
from spacy.lang.es import Spanish
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
from datetime import datetime
import pyprind
from isef_charts import generate_isef_chart, generate_neg_pos_chart, generate_boxplot_chart
from functools import reduce
from isef_tfidf import get_word_matrix, get_freq_matrix, get_doc_freq, get_avg_freq, sortSecond
from math import log10
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn import preprocessing
from isef_wc_tone import getList_pos_neg_words, GroupedColorFunc

spacy.require_cpu()

def getFrequencyDictForText(sentence):
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    return tmpDict


# If a dictionary is passed as an argument, use it and assume random removal of words
if len(sys.argv)>1:
    RANDOM = True
    accented = False
    dict_file = sys.argv[1]
    df = pd.read_excel(f'../dictionary/{dict_file}')
    df_dict = df.copy()
    df_dict["Connotación"]=df_dict["Connotación"].apply(list)
    df_dict.rename(columns = {"Connotación": "sentiment"}, inplace=True) 
else:
    accented = True
    dict_file = "finalBdE_dict.xlsx"
    df = pd.read_excel(f'../dictionary/{dict_file}')
    df_dict = df[ (df["Connotación"]!="*") | (df["pos"]!=0) | (df["neg"]!=0)].copy()
    df_dict["Connotación"]=df_dict["Connotación"].apply(list)
    df_dict.rename(columns = {"Connotación": "sentiment"}, inplace=True) 
    # # remove columns
    # df_dict = df_dict.loc[:, ~df_dict.columns.isin(['pos','neg','neu'])]
    # distributions will be a list
    df_dict['distr']=df_dict[["pos","neu","neg"]].apply(lambda x: ['+'] * x['pos'] + ['*'] * x['neu'] + ['-'] * x['neg'],axis=1)

print(f"Usando diccionario {dict_file}")

# create dictionary from dataframe
sent_dict = df_dict.set_index('Palabra').T.to_dict()
spacy.require_cpu()
nlp = Spanish()  # just the language with no model
#matcher = PhraseMatcher(nlp.vocab)
matcher = Matcher(nlp.vocab)
if spacy.__version__ < '3.0.0':
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
else:
    # Spacy 3.0
    sentencizer = nlp.add_pipe("sentencizer")

# Matches 
print("Creando patrones...")
all_words = list(sent_dict.keys())
pattern1 = [{"ORTH": {"IN": all_words}}]

# Random words to exclude in the sampling. Will also be used to keep a counter of positive and negative matches (resets every file)
five_perc = int(len(all_words)*0.05)


print("Generando " + str(n_cases) + " casos...")
if RANDOM:
    for i in range(n_cases):
        r_words = random.sample(all_words, five_perc)
        for word in all_words:
            if word in r_words: # Make it neutral
                sent_dict[word]['sentiment'].append("*")
            else: # assign the default
                sent_dict[word]['sentiment'].append(sent_dict[word]['sentiment'][0])
else:
    for i in range(n_cases):
        for word in all_words:
            sent_dict[word]['sentiment'].append(random.choice(sent_dict[word]['distr']))

if spacy.__version__ < '3.0.0':
    matcher.add("word", None, pattern1)
else:
    matcher.add("word", [pattern1])

print("Iniciando bucle principal...")
sys.stdout.flush()



attrs = [{'file_pattern':'IEF%Y%m%d_all.txt',
          'file_name': "df_body",
          'folder':"body",
          'name':"cuerpo",
          'color':'rgb(27, 72, 139)'},
         {'file_pattern':'IEF%Y%m%d.txt',
          'file_name': "df_intro",
          'folder':'intro',
          "name":"introducción",
          'color':'rgb(245, 143, 36)'},
         {'file_pattern':'%Y%m%d.txt',
          'file_name': "df_newsp",
          'folder':'newsp',
          "name":"periódicos",
          'color':'rgb(99, 201, 212)'}]

path = get_application_path()

files = [[f for f in os.listdir(path + f"/../input/{p['folder']}/")] for p in attrs]
num_files = reduce(lambda count, l: count + len(l), files, 0)
# if PYPRIND:
#     bar = pyprind.ProgBar(num_files, bar_char='█',title='Progress',monitor=False)
# else:
#     bar = tqdm(total=num_files)

score_dict={}

# loop through the three file groups
for ind, attr in enumerate(attrs):
    text_list = []
    if len(files[ind])==0:
        continue
    file_pattern = attr["file_pattern"]
    folder = attr["folder"]
    
    df_file_name = f"../output/data/{attr['file_name']}"
    
    # Try to clean some typical OCR errors
    for f in files[ind]:
        with open (path + f"/../input/{folder}/{f}", "r", encoding='utf8') as myfile:
            body = myfile.read()
            body = re.sub( "([a-zA-ZáéíóúÁÉÍÓÚ])-\s*([áéíóúa-zñ])",r"\1\2", body)
            body = re.sub( "([a-zA-ZáéíóúÁÉÍÓÚ])¬\s*([áéíóúa-zñ])",r"\1\2", body)
            body = re.sub("¬", "", body)
            body = re.sub("ofi cinas", "oficinas", body)
            body = re.sub("apesar", "a pesar", body)
            body = re.sub("zooz", "2002", body)
            body = re.sub("lafalta", "la falta", body)
            body = re.sub("induye", "incluye", body)
            body = re.sub("mediabaja", "media baja", body)    
            body = re.sub("frtanciación", "financiación", body)
            body = re.sub(" dalas", " de las", body)
            text_list += [[f, body]]


    
    # Perform the tally for this series
    bar = pyprind.ProgBar(len(text_list), bar_char='█',title=f'Cálculo de ISEF para {attr["folder"]}',monitor=False)
    df_sent, index_range, index_df = count_words(nlp, text_list, sent_dict,file_pattern, bar, matcher, accented)

    print("Calculando pendientes, filtrado, consolidado y guardando...")
    min_t = index_df["date"].min()
    if min_t.month >=7:
        month = "07"
    else:
        month = "01"
    min_t = f"{min_t.year}-{month}-01"
    index_df["secvalue"]=index_df["date"].apply(lambda x: (pd.to_datetime(x)-pd.to_datetime(min_t)).days/100)

    for j in range(n_cases):
        i_df = index_df.loc[index_df.i==j,('score','secvalue')]
        index_df.loc[index_df.i==j,('slope')]=i_df['score'].diff()/i_df["secvalue"].diff()
   
    index_range = pd.DataFrame(index_range, columns=["filename", "max", "min"])
    
    # calculate date of the index range from the name of the report
    index_range["date"] = index_range['filename'].apply(lambda x: datetime.strptime(x,file_pattern))

    # Filter and groupby

    # Filter only the sentences with positive or negative sentiment
    df_filt = df_sent.query('negative>=1 | positive>=1')
    #df_filt = df_sent.query('negative>=0 | positive>=0')

    # Save file to storage without new lines
    df_filt = df_filt.replace(to_replace='\n', value=' ', regex=True)
    #df_filt.to_csv(df_file_name + "_points.xlsx", index = False)
    df_filt.to_excel(f"{df_file_name}" + "_score.xlsx", index = False)
    
    # group by FSR
    df_FSI = df_sent.groupby(['filename'], as_index=False)[['positive','negative']].agg('sum')
    
    # Calculate index
    df_FSI["index"] = (df_FSI["negative"] - df_FSI["positive"])/(df_FSI["positive"]+df_FSI["negative"])
    
    # Calculate date of he index from the name of the report
    df_FSI["date"] = df_FSI['filename'].apply(lambda x: datetime.strptime(x, file_pattern))
    
    
    # Save files to COS
    index_df.to_csv(df_file_name +"_boxplot.csv", index=False)
    df_FSI.to_csv(df_file_name +".csv", index = False)
    index_range.to_csv(df_file_name + "_range.csv", index = False)
    
    # Generate charts
    generate_isef_chart(df_FSI, attr)

    # Wordcloud
    if WORDCLOUD:
        # Fix some lemmas in their form that are more common in this context
        if spacy.__version__ < '3.0.0':
            table = nlp.vocab.lookups.get_table('lemma_lookup')
        elif not nlp.has_pipe("lemmatizer"):
            # spaCy 3 uses rules based on pos by default for Spanish lemmatizer
            lemma_config = {"mode":"lookup"}
            # https://spacy.io/api/lemmatizer
            lemmatizer = nlp.add_pipe("lemmatizer", config = lemma_config)
            nlp.initialize()
            table = lemmatizer.lookups.get_table('lemma_lookup')
    
        new_lemmas = [["los", "el"],["regulatorios", "regulatorio"], 
                      ["carbono", "carbono"], ["azufre", "azufre"], 
                      ["medio", "medio"], ["la","el"],
                      ["española", "español"], ["acciones", "acción"],
                      ["españolas", "español"],
                      ["para", "para"], ["prima", "prima"],
                      ["largo", "largo"], ["regulatorios", "regulatorio"],
                      ["parís", "parís"], ["precio", "precio"],
                      ["las", "el"], ["dos", "dos"],
                      ["g", "g"], 
                      ["ml", "moneda local"],["anl", "actividad no local"], 
                      ["mnl", "moneda no local"], ["matrices", "matriz"], 
                      ["otoño", "otoño"]]
        for tup in new_lemmas:
            table.set(tup[0], tup[1])    
        
        if spacy.__version__ < '3.0.0':
            nlp.vocab.lookups.remove_table("lemma_lookup")
            nlp.vocab.lookups.add_table('lemma_lookup',table) 
        
    
        # For each IEF , create a list of words and lemmas
        word_matrix = get_word_matrix(text_list, nlp)
        # For each IEF, create a dictionary with the count of lemmas
        freq_matrix = get_freq_matrix(word_matrix)
        # Calculate the document frequency of each word
        doc_freq = get_doc_freq(freq_matrix)
        avg_freq = get_avg_freq(freq_matrix)
        score_dict[attr['file_name']] = {}
        tuple_list = []
        bar = pyprind.ProgBar(len(freq_matrix), bar_char='█',title=f'TFIDF para {attr["folder"]}',monitor=False)
        for ief in freq_matrix:
            # Calculate the weighted  score for each word
            score = [[w, (1 + log10(freq_matrix[ief][w]))/(1 + log10(avg_freq[ief])) * log10(len(freq_matrix)/doc_freq[w])] for w in freq_matrix[ief]]
            bar.update() 
            # Calculate date of the index from the name of the report
            filedate = datetime.strptime(ief, file_pattern)
            score.sort(key = sortSecond, reverse = True)
            tuple = [[ief, filedate, word[0], word[1]] for word in score[0:25] ]
            tuple_list += tuple
        #display(freq_matrix)
        score_df = pd.DataFrame(tuple_list, columns=["filename","date","word", "score"])        
        score_df.to_csv(df_file_name +"_topics.csv")
        bar = pyprind.ProgBar(len(text_list), bar_char='█',title=f'Generación del Wordcloud para {attr["folder"]}',monitor=False)
        for ief in text_list:
            score_dict={key: value for (key, value) in score_df[score_df['filename']==ief[0]][['word','score']].values.tolist()}
            wordcloud = WordCloud(background_color="white").generate_from_frequencies(frequencies = score_dict)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            #plt.show()
            bar.update(item_id=ief[0])
            plt.savefig(f'../output/wordcloud/{ief[0][:-4]}.png', bbox_inches='tight')
            plt.close()

    # Negativity and Positivity charts
    tuple_list = []
    bar = pyprind.ProgBar(len(text_list), bar_char='█',title=f'Conteo de palabras totales para {attr["folder"]}')
    for row in text_list:
        (filename, body) = row
        bar.update(item_id=filename)
        doc = nlp(body)
        #print(filename, len(doc1), len(doc2))
        tuple = [[filename,len([[t, t.is_punct] for t in doc if t.is_alpha == True ])]]
        tuple_list += tuple
    df_words = pd.DataFrame(tuple_list, columns=["filename", "num_words"])
    df_words.to_excel(f"{df_file_name}" + "_words.xlsx", index = False)
    # Create the Scaler object
    scaler = preprocessing.MinMaxScaler(feature_range = (-1,1))
    df_FSI = pd.concat([df_FSI, df_words], axis=1)
    df_FSI['positivity'] = df_FSI['positive']/(df_FSI['num_words'])
    df_FSI['negativity'] = df_FSI['negative']/(df_FSI['num_words'])
    generate_neg_pos_chart(df_FSI, attr)
    generate_boxplot_chart(index_df, df_FSI, attr)

    # Word Cloud by Tone
    bar = pyprind.ProgBar(len(text_list), bar_char='█',title=f'Generación de wordclouds por tonalidad {attr["folder"]}')
    for row in text_list:
        (file_str, body) = row
        bar.update(item_id=file_str)
        # Get the words with sentiment for the selected df and filename
        list_pos, list_neg = getList_pos_neg_words(df_filt, file_str)
        # Generate word clouds
        nube_text = ' '.join(list_pos+list_neg) # from list to string again
        # wc = WordCloud(background_color="white", max_font_size=40).generate(nube_text) # reduce font size
        wc = WordCloud(background_color="white").generate_from_frequencies(getFrequencyDictForText(nube_text))
        # change color following this mapping
        color_to_words = {
            # positive words will be colored with green
            '#00ff00': list_pos,
            # negative words will be colored with red
            'red': list_neg }
        grouped_color_func = GroupedColorFunc(color_to_words)
        wc.recolor(color_func=grouped_color_func)
        # plot word cloud
        plt.figure()
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        # plt.show()
        plt.savefig('../output/wc_tone/{}.png'.format(file_str[:-4]), bbox_inches='tight')
        plt.close()

print("Proceso finalizado. Verifique que se han generado los gráficos y ficheros en las carpetas correspondientes.")