# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 13:17:07 2022

@author: q31487
"""
import pandas as pd
import scipy
from sklearn import preprocessing

resultados_body = r"..\output\data\df_body_score.xlsx"
diccionario = r"..\dictionary\finalBdE_dict.xlsx"
resultados_intro = r"..\output\data\df_intro_score.xlsx"

df_dict = pd.read_excel(diccionario)
df_comb_body = pd.read_excel(resultados_body)
df_comb_intro = pd.read_excel(resultados_intro)


counter = { pal:0 for pal in df_dict["Palabra"].to_list()}
palabras = ([p for p in df_comb_body["pos_words"].dropna().to_list()] +
           [p for p in df_comb_body["neg_words"].dropna().to_list()] )

# Uncomment to include intros
palabras = palabras + ([p for p in df_comb_intro["pos_words"].dropna().to_list()] +
            [p for p in df_comb_intro["neg_words"].dropna().to_list()] )


palabras = [p for sublist in palabras for p in sublist.split(", ")]

for palabra in palabras:
    counter[palabra] += 1

df_cont = pd.DataFrame.from_dict(counter, orient="index", columns=["frecuencia"])
df_dict = df_dict.set_index("Palabra")
df_res = pd.merge(df_dict, df_cont, left_index=True, right_index=True)
df_res.sort_values(["frecuencia"], ascending=False, inplace=True)
df_res.to_excel(r"..\output\data\frecuencias.xlsx")
