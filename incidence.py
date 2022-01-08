import os
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator

from utilities import ressource_path, downloadfiles, removefiles, readjson


def initialiserincidence(path, urls):
    incid = Incidence()
    for code in [11, 12]:
        url = next(x for x in urls if x['code'] == code)
        incid.readfile(path, url['name_csv'], url['admin'])
    return incid


def calculerincidence(incid, admin, classe, plot=True):
    incid.extrairedata(admin, classe)
    if plot:
        incid.plot(classe, tag='incid')


class Incidence:
    def __init__(self):
        self.data = dict()
        self.incidence = None

    def readfile(self, path, file, tag):
        self.data[tag] = pd.read_csv(os.path.join(path, file), delimiter=';')

    def extrairedata(self, admin, classe, codeadmin=None):
        if admin == 'fra':
            self.extrairedatafr(classe)
        elif admin == 'reg':
            self.extrairedatareg(classe, codeadmin)
        elif admin == 'dep':
            self.extrairedatadep(classe, codeadmin)

    def extrairedatafr(self, classe):
        df = self.data['fra'].groupby('cl_age90').get_group(classe).copy()
        time = pd.to_datetime(df['jour'])
        df.drop(labels=['fra', 'jour', 'cl_age90', 'pop_f', 'pop_h', 'pop'],
                axis=1, inplace=True)
        df.set_index(time, inplace=True)
        df = df.resample('W').sum()
        # Extraire les populations des classes d age
        pop = self.data['fra'].groupby(by='cl_age90').apply(
            lambda x: x[['pop_f', 'pop_h', 'pop']].iloc[0])
        # Calcul de l'incidence
        df.loc[:, 'incid_h'] = df.loc[:, 'P_h'] / pop.loc[
            classe, 'pop_h'] * 100000
        df.loc[:, 'incid_f'] = df.loc[:, 'P_f'] / pop.loc[
            classe, 'pop_h'] * 100000
        df.loc[:, 'incid'] = df.loc[:, 'P'] / pop.loc[
            classe, 'pop'] * 100000
        df.dropna(inplace=True)
        self.incidence = copy.deepcopy(df)

    def extrairedatareg(self, classe, codeadmin):
        print('toto')

    def extrairedatadep(self, classe, codeadmin):
        print('toto')

    def plot(self, classe, tag='incid'):
        fig, ax1 = plt.subplots(figsize=(15, 15))
        indexes = np.arange(self.incidence.shape[0])
        ax1.bar(indexes - 0.15, height=self.incidence[tag],
                width=0.3, color='red', label="Taux d'incidence")
        ax1.set_ylabel('Taux d incidence')
        ax1.set_xticks(indexes.tolist())
        ax1.set_xticklabels(self.incidence.index.strftime('%Y/%m/%d'), rotation=45)
        ax1.xaxis.set_major_locator(MultipleLocator(4))
        ax1.xaxis.set_minor_locator(MultipleLocator(1))
        ax1.set_title("Taux d'incidence pour la classe d'age {}".format(classe))
        ax1.legend()


class Population:
    def __init__(self, path, urls):
        self.data = dict()
        self.popfr = None
        self.popreg = dict
        for code in [11, 12]:
            url = next(x for x in urls if x['code'] == code)
            self.readfile(path, url['name_csv'], url['admin'])

    def readfile(self, path, file, tag):
        self.data[tag] = pd.read_csv(os.path.join(path, file), delimiter=';')

    def extrairepopulation(self, coderegion=None):
        if coderegion:
            return self.data['reg'].groupby(by='reg').get_group(
                coderegion).gro
            upby(by='cl_age90').apply(
                lambda x: x[['pop_f', 'pop_h', 'pop']].iloc[0])
        else:
            return self.data['fra'].groupby(by='cl_age90').apply(
            lambda x: x[['pop_f', 'pop_h', 'pop']].iloc[0])





if __name__ == "__main__":
    path = ressource_path('data')
    fileurls = 'urls.cfg'
    urls = readjson(path, fileurls)
    dl = False
    if dl:
        removefiles(path)
        downloadfiles(path, urls)
    # Incidence
    admin = 'fra'
    classes = [9, 49, 0]
    # Initialiser
    incid = initialiserincidence(path, urls)
    for cl in classes:
        calculerincidence(incid, admin, cl)
    plt.show()
    print('toto')