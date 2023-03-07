# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:21:50 2020

@author: q31487
"""

import sys
from math import log10
import pandas as pd
import pyprind
#lemma_lookup = nlp.vocab.lookups.get_table("lemma_lookup")

def lemma_lookup(w):
    return lemmatizer.lookup(w) 
#    doc = nlp.make_doc(w)
#    return doc[0].lemma_

def get_word_matrix(df, nlp):
    word_matrix = {}
    for row in df:
        filename, body = row[0], row[1]
        body = body.lower()
        doc = nlp(body)
        word_matrix[filename] = [tk.lemma_ for tk in doc if tk.is_alpha]
    return word_matrix
    

def get_freq_matrix(word_matrix):
    # Iterate through each FSR
    freq_matrix = {}
    for filename in word_matrix:
        stop = set(['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 'estén', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría', 'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas', 'estábamos', 'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais', 'estuvieran', 'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha', 'hemos', 'habéis', 'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá', 'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 'hubisteis', 'hubieron', 'hubiera', 'hubieras', 'hubiéramos', 'hubierais', 'hubieran', 'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen', 'habiendo', 'habido', 'habida', 'habidos', 'habidas', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 'seas', 'seamos', 'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 'sería', 'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais', 'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras', 'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen', 'sintiendo', 'sentido', 'sentida', 'sentidos', 'sentidas', 'siente', 'sentid', 'tengo', 'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 'tengáis', 'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos', 'tendréis', 'tendrán', 'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía', 'tenías', 'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran', 'tuviese', 'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo', 'tenido', 'tenida', 'tenidos', 'tenidas', 'tened'])
        stop.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '@', '#', 'rt', 'amp','pues', 'aunque','entidad', 'entidades', 'españolas', 'españa', 'español', '_', 'oct', 'bien', 'jun', 'dic'])
        stop.update(["enero", "febrero","marzo","sep","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre", "otoño","bde"])
        freq_matrix[filename] = {}
        for tk in word_matrix[filename]:
            if tk in stop:
                continue
            elif tk in freq_matrix[filename]:
                freq_matrix[filename][tk] += 1
            else:
                freq_matrix[filename][tk] = 1
    return freq_matrix
    

def get_doc_freq(freq_matrix):
    """Calculate for each word in how many documents
it appears.
"""
    doc_freq = {}
    for f in freq_matrix:
        for w in freq_matrix[f]:
            # check if the word is in the document
                # count the documents in which the lemma appears
                if w in doc_freq:
                    doc_freq[w] += 1
                else:
                    doc_freq[w] = 1
    return doc_freq       

def get_avg_freq(freq_matrix):
    avg_freq = {}
    for f in freq_matrix:
        avg_freq[f] = sum(freq_matrix[f].values())/len(freq_matrix[f])
    return avg_freq    
    
def get_score(sent_list, terms_freq, doc_freq, a, N, word_list):
    score_neg=0
    score_dict = {}
    for i, w in enumerate(word_list):
        w = w[0]
        if w in sent_list:
            # Check for negation of the term
            if any(x in [word_list[i-3][0], word_list[i-2][0], word_list[i-1][0]] for x in ["menos","no","nunca", "sin", "pérdida", "disminución"]): 
                negate = True
            else:
                negate = False        
            #if w in terms_freq:
            wl = lemma_lookup(w)
            if w in score_dict:
                score_dict[w] += (1 + log10(terms_freq[wl]))/(1 + log10(a)) * log10(N/doc_freq[w])
            else:
                score_dict[w] = (1 + log10(terms_freq[wl]))/(1 + log10(a)) * log10(N/doc_freq[w])
                if score_dict[w] <0:
                    print(w, wl,score_dict[w],terms_freq[wl],a,N,doc_freq[wl])
            # only positive words can become negative
            if negate and change_sign:
                score_neg += (1 + log10(terms_freq[wl]))/(1 + log10(a)) * log10(N/doc_freq[w])
            elif not negate:
                score += (1 + log10(terms_freq[wl]))/(1 + log10(a)) * log10(N/doc_freq[w])
    return score, score_neg, score_dict

def sortSecond(val): 
    return val[1]  

