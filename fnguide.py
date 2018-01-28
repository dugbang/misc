"""
http://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&gicode=A000660&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701
"""
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup

import os.path
import time
import random
import pickle


def get_dates(soup):
    dates = []
    for d2 in soup.findAll('tr', {'class': 'td_gapcolor2'}):
        for d3 in d2.findAll('div'):
            dates.append(d3.text)
    return dates


def get_names(soup):
    names = []
    for d2_2 in soup.findAll('th', {'class': 'clf'}):
        for d3_2 in d2_2.findAll('div'):
            if d3_2.text.strip() != 'IFRS(연결)':
                names.append(d3_2.text.strip())
    return names


def get_values(soup):
    values = []
    for d2_3 in soup.findAll('td', {'class': 'r'}):
        values.append(d2_3.text)
    return values


def fnguide(fname='d:/Documents/etf1.0/000020.html'):
    # fname = 'd:/Documents/etf1.0/000020.html'
    html = open(fname, 'r', encoding='utf8').read()

    soup = BeautifulSoup(html, 'html.parser')

    for d0 in soup.findAll('div', {'class': 'um_table', 'id': 'highlight_D_Y'}):
        for d1 in d0.findAll('table', {'class': 'us_table_ty1 h_fix zigbg_no'}):
            dates = get_dates(d1)
            assert len(dates) == 8
            names = get_names(d1)
            assert len(names) == 24
            values = get_values(d1)
            assert len(values) == 8 * 24
            break

    # print(dates)
    # print(names)
    # print(values)

    records = []
    for i in range(len(dates)):
        rec = []
        for j in range(len(names)):
            rec.append(values[i + j * len(dates)])

        records.append(rec)
        # print(rec)
        # break

    for r in records:
        print(r)


FNGUIDE_URL = 'http://comp.fnguide.com/SVO2/asp/SVD_Main.asp?pGB=1&gicode=A{}&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701'
FNGUIDE_URL_FIN = 'http://comp.fnguide.com/SVO2/asp/SVD_Finance.asp?pGB=1&gicode=A{}&cID=&MenuYn=Y&ReportGB=&NewMenuID=103&stkGb=701'
FNGUIDE_URL_FINRATE = 'http://comp.fnguide.com/SVO2/asp/SVD_FinanceRatio.asp?pGB=1&gicode=A{}&cID=&MenuYn=Y&ReportGB=&NewMenuID=104&stkGb=701'
FNGUIDE_URL_INVEST = 'http://comp.fnguide.com/SVO2/asp/SVD_Invest.asp?pGB=1&gicode=A{}&cID=&MenuYn=Y&ReportGB=&NewMenuID=105&stkGb=701'

BASE_FNGUIDE_PATH = 'd:/Documents/_date/fnguide/'

FNGUIDE_URL_LIST = (FNGUIDE_URL, FNGUIDE_URL_FIN, FNGUIDE_URL_FINRATE, FNGUIDE_URL_INVEST)
FNGUIDE_URL_LIST_NAME = ('main', 'finance', 'financeRatio', 'invest')


def save_html_fnguide(date_str):

    if not os.path.exists(BASE_FNGUIDE_PATH + date_str):
        os.mkdir(BASE_FNGUIDE_PATH + date_str)

    def code_download():
        for i_, url_addr in enumerate(FNGUIDE_URL_LIST):
            filename = BASE_FNGUIDE_PATH + '{}/{}_{}.html'.format(date_str, code, FNGUIDE_URL_LIST_NAME[i_])
            if not os.path.exists(filename):
                print(filename)
                try:
                    html = urlopen(url_addr.format(code))
                except TimeoutError:
                    time.sleep(random.randrange(304, 309))
                    html = urlopen(url_addr.format(code))

                with open(filename, 'wb') as fp:  # 자동으로 close() 를 호출함....
                    fp.write(html.read())
                time.sleep(random.randrange(4, 9))

    codes = pickle.load(open('d:/Documents/_date/code_list.dump', 'rb'))
    k = len(codes)
    i = 0
    for c in codes:
        i += 1
        if type(c) == tuple:
            code = c[0]
        else:
            code = c
        # if i > 4:
        #     break

        cur_tm = time.localtime()
        print('fnguide download; %s, %4d/%4d => %6.2f%%, printed time; %02d:%02d' %
              (code, i, k, i * 100 / k, cur_tm.tm_hour, cur_tm.tm_min))

        # if code > '004690':   continue
        code_download()


if __name__ == "__main__":
    t = time.time()

    # fnguide()  # read page information...
    date_str = datetime.date.today().strftime('%Y%m%d')
    print(date_str)
    save_html_fnguide(date_str)

    tm = time.localtime()
    process_time = (time.time() - t)
    if process_time < 100:
        print(__file__, 'Python Elapsed %.02f seconds, current time; %02d:%02d' %
              (process_time, tm.tm_hour, tm.tm_min))
    elif process_time < 6000:
        print(__file__, 'Python Elapsed %.02f minute, current time; %02d:%02d' %
              (process_time / 60, tm.tm_hour, tm.tm_min))
    else:
        print(__file__, 'Python Elapsed %.02f hours, current time; %02d:%02d' %
              (process_time / 3600, tm.tm_hour, tm.tm_min))
