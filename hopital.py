import os
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator

from utilities import ressource_path, downloadfiles, removefiles, readjson
from incidence import Population


def initialiserhopital(path, urls):
    hop = Hopital(path, urls)
    for code, type in zip([0, 3], ['nouveaux', 'hosp']):
        url = next(x for x in urls if x['code'] == code)
        hop.readfile(url['name_csv'], type)
    hop.attribuerdata()
    return hop


def calculerhopital(hop, tag, classe, coderegion=None):
    df = hop.extrairedata(tag, classe, coderegion)
    hop.plot(df, tag, classe)


class Hopital:
    def __init__(self, path, urls):
        self.path = path
        self.urls = urls
        self.pop = Population(path, urls)
        self.data = dict()
        self.hosp = None
        self.rea = None
        self.dc = None
        self.nouveauxcas = None
        self.nbhosp = dict()
        self.pcthosp = dict()
        self.nbmort = dict()
        self.pctmort = dict()
        self.letalite = dict()


    def readfile(self, file, tag):
        self.data[tag] = pd.read_csv(os.path.join(self.path, file), delimiter=';')

    def attribuerdata(self):
        self.nouveauxcas = self.data['nouveaux'].copy()
        self.hosp = self.data['hosp'][['reg', 'jour', 'cl_age90', 'hosp']].copy()
        self.rea = self.data['hosp'][['reg', 'jour', 'cl_age90', 'rea']].copy()
        self.dc = self.data['hosp'][['reg', 'jour', 'cl_age90', 'dc']].copy()

    def extrairedata(self, tag, classe, coderegion):
        if coderegion:
            return self.extrairedatareg(coderegion, tag, classe)
        else:
            return self.extrairedatafr(tag, classe)

    def calculerindicateurs(self, coderegion):
        if coderegion:
            self.calculerindicateursreg(coderegion)
        else:
            self.calculerindicateursfr()

    def calculerindicateursreg(self, code):
        print('toto')

    def calculerindicateursfr(self):
        # Extraction du nombre de décès
        lastday = self.data['hosp'].tail(1)['jour'].values[0]
        dc = self.data['hosp'].groupby(by='jour', sort=False).get_group(
            lastday).groupby(by='cl_age90')['dc'].apply(sum)
        for cl in [9, 19, 29, 39, 49, 59, 69, 79, 89, 0]:
            self.nbhosp[str(cl)] = \
            self.nouveauxcas.groupby(by='cl_age90', as_index=False).get_group(
                cl).groupby(by='Semaine')['NewAdmHospit'].apply(sum).sum()
            self.pcthosp[str(cl)] = self.nbhosp[str(cl)] / \
                                    self.pop.extrairepopulation().loc[
                                        cl, 'pop'] * 100
            self.nbmort[str(cl)] = dc[cl]
            self.pctmort[str(cl)] = dc[cl] / \
                                    self.pop.extrairepopulation().loc[
                                        cl, 'pop'] * 100
            self.letalite[str(cl)] = self.nbmort[str(cl)] / self.nbhosp[str(cl)] *100


    def extrairedatafr(self, tag, classe):
        if tag == 'nouveauxcas':
            return self.__getattribute__(tag).groupby('cl_age90').get_group(
                classe).groupby(by='Semaine')['NewAdmHospit'].apply(sum).copy()
        elif tag == 'dc':
            df = self.__getattribute__(tag).groupby('cl_age90').get_group(
                classe).groupby(by='jour')[tag].apply(sum).diff()
            df.index = pd.to_datetime(df.index)
            return df.resample('W').sum()
        else:
            df = self.__getattribute__(tag).groupby('cl_age90').get_group(
                classe).groupby(by='jour')[tag].apply(sum).copy()
            time = pd.to_datetime(df.index)
            df.index = time
            return df

    def extrairedatareg(self, tag, classe):
        print('toto')

    def plot(self, df, tag, classe):
        fig, ax1 = plt.subplots(figsize=(15, 15))
        if tag == 'nouveauxcas':
            label = df.index
            title = "Nombre total de personnes hospitalisées " \
                    "depuis Mars 2020 dans la classe {}: {}".format(classe, df.sum())
        else:
            label = df.index.strftime('%Y/%m/%d')
            title = "{} pour la classe d'âge {}".format(tag, classe)
        ax1.set_title(title)
        indexes = np.arange(df.shape[0])
        ax1.set_xticks(indexes.tolist())
        ax1.set_ylabel(tag)
        if tag in ['nouveauxcas', 'dc']:
            ax1.bar(indexes - 0.15, height=df.values,
                    width=0.3, color='red', label=tag)
            ax1.set_xticklabels(label, rotation=45)
            ax1.xaxis.set_major_locator(MultipleLocator(4))
        else:
            ax1.plot(indexes, df.values, label=tag)
            ax1.set_xticklabels(label, rotation=45)
            ax1.xaxis.set_major_locator(MultipleLocator(30))
        ax1.xaxis.set_minor_locator(MultipleLocator(1))
        ax1.legend()


if __name__ == "__main__":
    path = ressource_path('data')
    fileurls = 'urls.cfg'
    urls = readjson(path, fileurls)
    dl = False
    if dl:
        removefiles(path)
        downloadfiles(path, urls)
    # Hopital
    tag = 'nouveauxcas'
    classes = [0, 9, 19, 29, 39, 49, 59, 69, 79, 89]
    coderegion = None
    # Initialisation et attribution des données
    hop = initialiserhopital(path, urls)
    hop.calculerindicateurs(coderegion)
    print("HOSP: {}".format(hop.nbhosp))
    print("MORTS: {}".format(hop.nbmort))
    print("HOSP %: {}".format(hop.pcthosp))
    print("MORTS %: {}".format(hop.pctmort))
    print("LETALITE %: {}".format(hop.letalite))
    for cl in classes:
        calculerhopital(hop, tag, cl, coderegion=coderegion)
    plt.show()
    print('toto')