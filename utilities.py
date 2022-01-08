# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 16:17:05 2019

@author: jerome.jacq
"""

import os
import sys
import json
import ssl

import pandas as pd


def readjson(path, file):
    with open(os.path.join(path, file), 'r', encoding='utf8') as fp:
        return json.load(fp)

def ressource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        if relative_path:
            return os.path.join(os.path.abspath('.'), relative_path)
        else:
            return os.path.abspath('.')


def removefiles(path):
    files = [x for x in os.listdir(path)
             if os.path.isfile(os.path.join(path, x))
             and x != 'region2020.csv' and x != 'urls.cfg']
    for file in files:
        os.remove(os.path.join(path, file))


def downloadfiles(path, urls):
    ssl._create_default_https_context = ssl._create_unverified_context
    for url in urls:
        df = pd.read_csv(url['url'], delimiter=';', low_memory=False)
        df.drop_duplicates(keep='last', ignore_index=True, inplace=True)
        df.dropna(inplace=True)
        # col = df.columns[0]
        # if col != 'fra':
        #     df = df.astype({df.columns[0]: int})
        # sauvegarde des données
        savefilenamedata = os.path.join(path, url['name_csv'])
        df.to_csv(savefilenamedata, sep=';', index=False)


def downloaddata(pathappdata, url, nomsauvegarde):
    """ télécharge et sauvegarde les données de santé publique france
    """
    # téléchargement des fichiers
    try:
        df = pd.read_csv(url, delimiter=';', low_memory=False)
    except pd.errors.ParserError:
        df = pd.read_excel(url)
    df.drop_duplicates(keep='last', ignore_index=True, inplace=True)
    df.dropna(inplace=True)
    col = df.columns[0]
    if col != 'fra':
        df = df.astype({df.columns[0]: int})
    # sauvegarde des données
    savefilenamedata = os.path.join(pathappdata, nomsauvegarde)
    df.to_csv(savefilenamedata, sep=';', index=False)

    return df
