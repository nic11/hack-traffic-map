from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re


html = open('table_matches.html').read()
soup = BeautifulSoup(html, 'html5lib')

table_matches = soup.find(class_='tournament-description')


mp_stadiums = {'Luzhniki Stadium': ('Moscow', 81006),
               'Saint Petersburg Stadium': ('Petersburg', 68134),
               'Fisht Stadium': ('Sochi', 47659),
               'Volgograd Stadium': ('Volgograd', 45568),
               'Nizhny Novgorod Stadium': ('Nizhny Novgorod', 45331),
               'Rostov-on-Don Stadium': ('Rostov-on-Don', 45145),
               'Kazan Arena': ('Kazan', 45105),
               'Samara Stadium': ('Samara', 44807),
               'Saransk Stadium': ('Saransk', 44442),
               'Otkrytiye Arena': ('Moscow', 44000),
               'Ekaterinburg Stadium': ('Yekaterinburg', 35696),
               'Kaliningrad Stadium': ('Kaliningrad', 35212)}


def make_date(date):
    date_slash, hhmm1 = date.split(' ')
    dd, mon, yyyy = date_slash.split('/')
    hh, mm = map(int, hhmm1.split(':'))
    return yyyy + '-' + mon + '-' + dd + 'T' + str(hh - 1).zfill(2) + ':' + str(mm).zfill(
        2) + ':00.000Z'


exp_stadium_arena = '(Arena)|(Stadium)'
exp_countries = '( – )|( - )'
exp_date = r'\d{2}'
bigdata = []
tr_tables = table_matches.find_all('tr')
for cur_tr in tr_tables:
    tds = cur_tr.find_all('td')
    if len(tds) == 0:
        continue

    stadium = tds[0].find(text=re.compile(exp_stadium_arena)).strip()
    countries = tds[1].find(text=re.compile(exp_countries))
    if countries is None:
        continue
    date = tds[3].find(text=re.compile(exp_date)).strip()
    country_list = list(map(lambda x: x.strip(), re.split('-|–', str(countries.strip()))))
    bigdata.append([mp_stadiums[stadium][0], stadium, mp_stadiums[stadium][1], country_list[0],
                    country_list[1],
                    make_date(str(date))])

frame = pd.DataFrame(bigdata,
                     columns=["City", "Stadium", "Capacity", "Country1", "Country2", "date"])

open('table_matches_json', 'w').write(frame.to_json())
open('table_matches_csv', 'w').write(frame.to_csv())
