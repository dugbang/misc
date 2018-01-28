"""
첫 페이지에서 링크를 찾아 저장한 후 링크에 접근하여 하위 링크를 찾아간다.
naver 의 웹 페이지를 html 로 저장한 후에 불러와야 한다.
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup

import os.path
import time

import random
import re

BASE_NAVER_PATH = 'd:/Documents/_date/naver/'
BASE_NAVER_URL = 'http://finance.naver.com/research/'
HTML_HEADER = '<!DOCTYPE html>\n'


def save_html(url_read, filename):
    # url_read = urlopen(base_naver_url + 'market_info_list.nhn')
    with open(BASE_NAVER_PATH + filename, 'wb') as fp:
        fp.write(HTML_HEADER.encode('utf-8'))  # 없으면 파싱이 되지 않음.
        fp.write(url_read.read().decode('euc-kr', 'replace').encode('utf-8', 'replace'))

    return open(BASE_NAVER_PATH + filename, 'r', encoding='utf8').read()


def get_url_and_filename(soup, fname_header, front_re_compile):
    for page_link in soup.findAll('a', href=front_re_compile):
        if 'href' in page_link.attrs:
            page_url = page_link.attrs['href']
            filename = '{}_{:05d}.html'.format(fname_header,
                                               int(page_link.attrs['href'][
                                                   page_link.attrs['href'].find('=') + 1:page_link.attrs['href'].find(
                                                       '&')]))
            # print(page_link.attrs['href'])
            # print('{}_{:05d}.html'.format(fname_header, int(page_link.attrs['href'][page_link.attrs['href'].find('=') + 1:
            #                                                                page_link.attrs['href'].find('&')])))
            break
    # market_info_read.nhn?nid=18933&page=1
    # market_info_18933.html
    print(page_url, filename)
    return page_url, filename


def market_info_download():
    front_head = 'market_info'
    front_page = 'market_info_list.nhn'
    front_re_compile = re.compile('^market_info_read.nhn?')
    html = save_html(urlopen(BASE_NAVER_URL + front_page), front_head)

    # soup = BeautifulSoup(html, 'html.parser')
    page_url, filename = get_url_and_filename(BeautifulSoup(html, 'html.parser'), front_head, front_re_compile)

    html = save_html(urlopen(BASE_NAVER_URL + page_url), filename)
    soup = BeautifulSoup(html, 'html.parser')

    for tmps1 in soup.findAll('p', {'class': 'source'}):
        # TODO; 타이틀 > 증권사, 등록일자...
        print(len(tmps1), tmps1.text)  # find('|')
    for tmps2 in soup.findAll('td', {'class': 'view_cnt'}):
        for tmps3 in tmps2.findAll('p'):
            # TODO; 내용...
            print(len(tmps3), tmps3, tmps3.text)

    for tmps in soup.findAll('div', {'class': 'report_list'}):
        for link in tmps.findAll('a', href=front_re_compile):
            # TODO; 다른 링크페이지 > 현재페이지와 비교하여야 함.
            if 'href' in link.attrs:
                print(link.attrs['href'])


def save_html_finance(page_num, front_head, front_re_compile):
    assert page_num > 0
    if not os.path.exists(BASE_NAVER_PATH + front_head):
        os.mkdir(BASE_NAVER_PATH + front_head)

    def save_page_link(soup):
        for link in soup.findAll('a', href=front_re_compile):
            if 'href' in link.attrs:
                url_addr = link.attrs['href']
                page_num_read = int(url_addr[url_addr.rfind('=') + 1:])
                if page_num != page_num_read:
                    return False

                filename = '{}_{:05d}.html'.format(front_head, int(url_addr[url_addr.find('=') + 1:url_addr.find('&')]))
                if os.path.exists(BASE_NAVER_PATH + front_head + '/' + filename):
                    return False

                if not os.path.exists(BASE_NAVER_PATH + front_head + '/' + filename):
                    cur_tm = time.localtime()
                    print('{}, {} > {:02d}:{:02d}'.format(page_num_read,
                                                          BASE_NAVER_PATH + front_head + '/' + filename,
                                                          cur_tm.tm_hour, cur_tm.tm_min))
                    try:
                        html_ = urlopen(BASE_NAVER_URL + url_addr)
                    except TimeoutError:
                        time.sleep(random.randrange(304, 309))
                    finally:
                        save_html(html_, front_head + '/' + filename)
                        time.sleep(random.randrange(4, 9))
        return True

    while True:
        page_url = BASE_NAVER_URL + '{}_list.nhn?&page={}'.format(front_head, page_num)
        html = save_html(urlopen(page_url), 'tmp.html')
        print(page_url)

        if not save_page_link(BeautifulSoup(html, 'html.parser')):
            print('end of list....')
            break

        time.sleep(random.randrange(60, 69))
        page_num += 1


if __name__ == "__main__":
    t = time.time()

    # market_info_download()

    save_html_finance(1, 'market_info', re.compile('^market_info_read.nhn?'))
    save_html_finance(1, 'invest', re.compile('^invest_read.nhn?'))
    save_html_finance(1, 'company', re.compile('^company_read.nhn?'))
    save_html_finance(1, 'industry', re.compile('^industry_read.nhn?'))
    save_html_finance(1, 'economy', re.compile('^economy_read.nhn?'))
    save_html_finance(1, 'debenture', re.compile('^debenture_read.nhn?'))

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
