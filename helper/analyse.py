from googletrans import Translator
import numpy as np
import pymorphy2
import numpy
import re
morph = pymorphy2.MorphAnalyzer()

translator = Translator()

def translate(text):
    return translator.translate(text, dest='ru').text

def standardize(text):
    text = text.replace("\\", " ").replace(u"╚", " ").replace(u"╩", " ")
    text = text.lower()
    text = re.sub('\-\s\r\n\s{1,}|\-\s\r\n|\r\n|\n', '', text)
    text = re.sub('[.,:;_%©?*,!@#$%^&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}|-|—', ' ', text)
    text = " ".join(morph.parse(str(word))[0].normal_form for word in text.split())
    text = ' '.join(word for word in text.split() if len(word)>1)
    text = text.encode("utf-8")
    return text

class Analyser:

    dictionary = {}
    vect_len = 0
    cat_len = 0
    categories = []
    v_categories = None

    def __init__(self, categories):
        self.categories = categories
        self.cat_len = len(categories)
        id = 0
        for categorie in categories:
            words = standardize(categorie).split()
            for word in words:
                if word not in self.dictionary:
                    self.dictionary[word] = id
                    id = id + 1

        self.vect_len = id
        v_categories = np.zeros((self.cat_len, self.vect_len))

        i = 0
        for categorie in categories:
            words = standardize(categorie).split()
            for word in words:
                if word in self.dictionary:
                    v_categories[i, self.dictionary[word]] = v_categories[i, self.dictionary[word]] + 1. / len(words)
            i = i + 1
        self.v_categories = v_categories
        return

    def analyse(self, text):
        vect = self.create_vect(text)
        distance = np.zeros(self.cat_len)
        for i in range(self.cat_len):
            distance[i] = self.dist(self.v_categories[i], vect[0:])
        return np.argmin(distance)

    # Creates vector
    def create_vect(self, text):
        vect = np.zeros(self.vect_len)
        words = standardize(translate(text)).split()
        length = len(words)
        for word in words:
            if word in self.dictionary:
                vect[self.dictionary[word]] = vect[self.dictionary[word]] + 1. / length
        return vect

    # Counts distance between two coordinates
    def dist(self, x,y):
        return numpy.sqrt(numpy.sum((x-y)**2))
