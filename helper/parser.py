from bs4 import BeautifulSoup
from analyse import *
import requests
import re
import sys
import sqlite3
import pickle
import logging
dictionary = []
counter = []
requirement = []

unicode = 'utf-8'
urls = [
            {
                'address':"https://jobs.ua/vacancy/page-%i",
                'tags':[
                    ['li','b-vacancy__item js-item_list '],
                    ['a', 'b-pager__link'],
                    ['div', 'b-vacancy-full__block b-text']
                ]
            },
            {
                'address':"https://talent.ua/vacancies/search/page%i",
                'tags':[
                    ['h2','card__title'],
                    ['li', 'last'],
                    ['div', 'advert__section']
                ]
            }
        ]

stop_words = [
    'описание', 'вакансия', 'знание', 'способность', 'учить', 'учиться', 'работа', 'по', 'на', 'до', 'приём', 'от'
]

def main():
    initialize()
    parse()
    finalize()
    return

def initialize():
    try:
        conn = sqlite3.connect('jatistic.db')
        cursor = conn.cursor()
        vacancies = cursor.execute('SELECT name FROM vacancies')
        for vacancy in vacancies:
            l, = vacancy
            dictionary.append(l)
            counter.append(0)
            requirement.append({})
    except:
        conn.close()
    conn.close()
    return

def parse():
    logging.basicConfig(filename='jparse.log', level=logging.INFO, filemode='w', format='%(message)s')
    v_an = Analyser(dictionary)
    for url in urls:
        i = 1
        buf = None
        errC = 0
        while True:
            try:
                request = requests.get(url['address'] % i)
                if int(request.status_code) != 200: break
                html = request.text.encode(request.encoding)
                soup = BeautifulSoup(html, 'lxml')
                vacancies = soup.find_all(url['tags'][0][0], url['tags'][0][1])
                if buf == vacancies and errC == 0 or errC >= 3: break
                buf = vacancies
                for l in vacancies:
                    id = v_an.analyse(l.find_all('a')[0].getText())
                    counter[id] += 1
                    request = requests.get(l.find_all('a')[0]['href'])
                    if(int(request.status_code) != 200): continue
                    html = request.text.encode(request.encoding)
                    soup = BeautifulSoup(html, 'lxml')
                    words = standardize(soup.find_all(url['tags'][2][0], url['tags'][2][1])[0].getText()).split()
                    for word in words:
                        if word not in stop_words:
                            if word not in requirement[id]:
                                requirement[id][word] = 1
                            elif requirement[id][word] < counter[id]:
                                requirement[id][word] += 1
                logging.info('OK ' + url['address'] % i)
            except Exception as e:
                logging.info("Error " + str(i))
                errC += 1
                if errC < 3: continue
                if errC > 5: break
            i = i + 1
            errC = 0
    return

def finalize():
    length = len(dictionary)
    try:
        conn = sqlite3.connect('jatistic.db')
        cursor = conn.cursor()
        for i in range(length):
            id = int(cursor.execute('SELECT id FROM vacancies WHERE name = ?', (dictionary[i],)).fetchone()[0])
            cursor.execute('INSERT INTO history VALUES (date(), ?, ?, ?)', (id, counter[i], pickle.dumps(requirement[i])))
            conn.commit()
    except:
        conn.close()
    conn.close()
    return

if __name__ == '__main__':
    main()
