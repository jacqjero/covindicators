import os
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.ticker import MultipleLocator

from utilities import ressource_path, downloadfiles, removefiles, readjson


def initialiserpositivite(path, urls):
    pos = Positivite()
    for code in [5, 6]:
        url = next(x for x in urls if x['code'] == code)
        pos.readfile(path, url['name_csv'], url['admin'])
    return pos


def calculerpositivite(pos, admin , classe):
    pos.extrairedata(admin, classe)
    pos.plot(classe, tag='pos')


class Positivite:
    def __init__(self):
        self.data = dict()
        self.positivite = None

    def readfile(self, path, file, tag):
        self.data[tag] = pd.read_csv(os.path.join(path, file), delimiter=';')

    def extrairedata(self, admin, classe, codeadmin=None, rolling=False):
        if admin == 'fra':
            self.extrairedatafr(classe)
        elif admin == 'reg':
            self.extrairedatareg(classe, codeadmin)
        elif admin == 'dep':
            self.extrairedatadep(classe, codeadmin)

    def extrairedatafr(self, classe):
        df = self.data['fra'].groupby('cl_age90').get_group(classe).copy()
        time = pd.to_datetime(df['jour'])
        df.set_index(time, drop=True, inplace=True)
        df.drop(labels=['fra', 'jour', 'cl_age90', 'pop'], axis=1, inplace=True)
        df = df.resample('W').sum()
        # self.positivite = copy.deepcopy(df.rolling(window=7).sum())
        df.loc[:, 'posh'] = df.loc[:, 'P_h'] / df.loc[:, 'T_h'] * 100
        df.loc[:, 'posf'] = df.loc[:, 'P_f'] / df.loc[:, 'T_f'] * 100
        df.loc[:, 'pos'] = df.loc[:, 'P'] / df.loc[:, 'T'] * 100
        df.dropna(inplace=True)
        self.positivite = copy.deepcopy(df)

    def extrairedatareg(self, classe, codeadmin):
        print('toto')

    def extrairedatadep(self, classe, codeadmin):
        print('toto')

    def plot(self, classe, tag='pos'):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 15))
        indexes = np.arange(self.positivite.shape[0])
        ax2.plot(indexes, self.positivite[tag])
        ax2.set_xticks(indexes.tolist())
        ax2.set_xticklabels(self.positivite.index.strftime('%Y/%m/%d'), rotation=45)
        ax2.xaxis.set_major_locator(MultipleLocator(4))
        ax2.xaxis.set_minor_locator(MultipleLocator(1))
        ax2.set_title(
            'Taux de positivité (%) pour la classe d age {}'.format(classe))
        ax11 = ax1.twinx()
        indexes = np.arange(self.positivite.shape[0])
        ax1.bar(indexes - 0.15, height=self.positivite['P'],
                width=0.3, color='red', label='Nb Test Positif')
        ax11.bar(indexes + 0.15, height=self.positivite['T'],
                 width=0.3, color='blue', label='Nb Total Test')
        ax1.set_ylabel('Nb Tests Positifs')
        ax11.set_ylabel('Nb Tests Total')
        ax1.set_xticks(indexes.tolist())
        ax1.set_title('Classe d age {}'.format(classe))
        ax1.set_xticklabels(self.positivite.index.strftime('%Y/%m/%d'), rotation=45)
        ax1.xaxis.set_major_locator(MultipleLocator(4))
        ax1.xaxis.set_minor_locator(MultipleLocator(1))
        bar1, labels = ax1.get_legend_handles_labels()
        bar2, labels2 = ax11.get_legend_handles_labels()
        ax1.legend(bar1 + bar2, labels + labels2, loc=0)


if __name__ == "__main__":
    path = ressource_path('data')
    fileurls = 'urls.cfg'
    urls = readjson(path, fileurls)
    dl = False
    if dl:
        removefiles(path)
        downloadfiles(path, urls)
    # Positivité
    admin = 'fra'
    classes = [0, 9, 49]
    # Initialiser positivite
    pos = initialiserpositivite(path, urls)
    for cl in classes:
        calculerpositivite(pos, admin, cl)

    plt.show()
    print('toto')