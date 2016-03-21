#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import sys
import time
import urllib
import requests
import datetime as dt
import xml.etree.ElementTree as et
import pandas as pd
import sqlite3

import mysetup as my

import pdb


class NicoCrawler:
    '''nicovideoから情報を取得するためのクローラー

    Example
    ============
    >>> ncrawler = NicoCrawler()
    >>> ncrawler.connect_sqlite('test.sqlite')
    '''

    def __init__(self, time_sleep=3, n_retry=10):
        self.time_sleep = time_sleep
        self.n_retry = n_retry

        self.session = requests.session()

        adapter = requests.adapters.HTTPAdapter(max_retries=self.n_retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.login()

    def __wait(self, times=1):
        time.sleep(times * self.time_sleep)

    def get_session(self, url, params={}):
        self.__wait()

        for n in range(self.n_retry):
            res = self.session.get(url, params=params)

            if res.status_code == 200:
                return res

            print('retry (get_session)')
            self.__wait(times=10*n)
        else:
            sys.exit('Exceeded self.n_retry (NicoCrawler.get_sesion())')

    def post_session(self, url, data):
        self.__wait()

        for n in range(self.n_retry):
            res = self.session.post(url, data=data)

            if res.status_code == 200:
                return res

            print('retry (post_session)')
            self.__wait(times=10*n)
        else:
            sys.exit('Exceeded self.n_retry (NicoCrawler.post_session())')

    def login(self):
        base_login = 'https://secure.nicovideo.jp/secure/login?site=niconico'
        self.post_session(base_login, data=my.login_dict)

    def connect_sqlite(self, filepath):
        self.con = sqlite3.connect(filepath)
        self.con.text_factory = str

    def __get_key_base(self, url, _dict={}):
        '''waybackkey, threadkey, getflvのretry機能の部分の関数
        '''
        for n in range(self.n_retry):
            key = self.get_session(url, params=_dict)

            if not 'error' in key.text:
                return key

            print('retry (__get_key_base)')
            self.__wait(times=10*n)
        else:
            sys.exit('Exceeded self.n_retry (NicoCrawler.__get_key_base())')

    def get_waybackkey(self, _dict):
        base_waybackkey = 'http://flapi.nicovideo.jp/api/getwaybackkey?'
        return self.__get_key_base(base_waybackkey, _dict)

    def get_threadkey(self, _dict):
        base_threadkey = 'http://flapi.nicovideo.jp/api/getthreadkey?'
        return self.__get_key_base(base_threadkey, _dict=_dict)

    def get_getflv(self, thread):
        base_getflv = 'http://flapi.nicovideo.jp/api/getflv/'
        return self.__get_key_base(base_getflv + str(thread))

    def get_html_text(self, url):
        '''urlが指定するページのhtmlを取得して返す
        '''
        res = self.get_session(url)
        return res.text

    def __get_url(self, thread, flapi_dict, options):
        getflv = self.get_getflv(thread)
        thread = re.findall('thread_id=(\d+)', getflv.text)[0]
        flapi_dict['thread'] = thread
        options['thread'] = thread

        threadkey = self.get_threadkey(flapi_dict)
        waybackkey = self.get_waybackkey(flapi_dict)
        
        getflv_text = urllib.request.unquote(getflv.text)
        url_server = re.findall(r'&ms=([^&]*)&', getflv_text)[0]
        base_get = url_server + 'thread?'
        
        url_get = '&'.join([base_get, urllib.parse.urlencode(options),
                            waybackkey.text, threadkey.text,
                            getflv.text])
        return url_get
        
    def __get_comments(self, thread, when_start='', n_comments=1000):
        '''threadを指定して，コメントが入っているxmlを返す

        Args
        ============
        thread : int
        when_start : string, optional (default='')
        n_comments : int, optional (default=1000)
            一度に取得するコメントの数
            1から1000までの整数を指定する
        '''
        flapi_dict = {
            'language_id': 0
        }

        options = {
            'version': 20061206,
            'res_from': -n_comments,
            'when': when_start,
            'scores': 1,
            'nicoru': 1,
        }

        for n in range(self.n_retry):
            url_get = self.__get_url(thread, flapi_dict, options)
            comments = self.get_session(url_get)
            
            if 'resultcode="0"' in comments.text:
                break
                
            print('retry (__get_comments)')
            self.__wait(times=10*n)
        else:
            sys.exit('Exceeded self.n_retry (__get_comments)')

        return comments

    def get_comments_of_thread(self, thread, title, when_start):
        '''指定したthreadの指定した範囲のコメントを取得する

        Example
        ============
        >>> thread = '1411545241'
        >>> when_start = int(time.mktime(dt.datetime.now().timetuple()))
        >>> db = ncrawler.get_comments_of_thread(thread, '', when_start)
        '''
        columns = ['score', 'nicoru', 'user_id', 'thread', 'no',
                   'date', 'mail', 'vpos', 'deleted', 'premium',
                   'text']

        comments = self.__get_comments(thread, when_start)
        etree = et.fromstring(comments.text.encode('utf-8'))
        children = etree.getchildren()

        data_list = []
        for child in children:
            child_dict = dict(child.items())
            if 'user_id' in child_dict:
                if child.text:
                    child_dict['text'] = (child.text
                                          .encode('ISO-8859-1')
                                          .decode('utf-8'))
                else:
                    child_dict['text'] = ''

                data_list.append(child_dict)

        if data_list:
            db = pd.DataFrame(data_list, columns=columns)
            db1 = db.fillna(0)
            db1 = db1.convert_objects(convert_numeric=True)
            db1.ix[:, 'title'] = title

            # pandas.DataFrame.convert_objectsで正しく変換されない列
            db1.ix[:, 'user_id'] = db.user_id
            db1.ix[:, 'mail'] = db.mail
            db1.ix[:, 'text'] = db.text

            return db1
        else:
            return []

    def get_all_comments_of_thread(self, thread, title, max_n_iter=1):
        '''指定したthreadのコメントを全て取得する．

        Args
        ============
        thread : int
            コメントを取得したい動画のthread_id
            (ex.1417589978)
        title : string
            コメントを取得したい動画のタイトル
            (ex. '牙狼＜GARO＞-炎の刻印-　第8話「全裸-FULL MONTY-」')
        max_n_iter : int, optional (default=0)
            取得を繰り返す回数
            デフォルトでは1回取得して終了する．
        '''
        db_list = []
        when_start = int(time.mktime(dt.datetime.now().timetuple()))
        n_iter = 1

        while True:

            db = self.get_comments_of_thread(thread, title, when_start)

            # 先頭のデータのdateがすでに取得してある or dbが<=0のとき
            if len(db) <= 0 or db.ix[0, 'date'] == when_start:
                break
            else:
                db_list.append(db)

            when_start = db.date.min()
            print('{0} --- {1}'.format(db.no.max(), db.no.min()))

            if n_iter >= max_n_iter:
                break

            n_iter += 1

        if db_list:
            db_list.reverse()
            db_all = pd.concat(db_list, ignore_index=True)
            db_all = db_all.drop_duplicates('no')

            db_all.to_sql('comments', self.con, index=False,
                          if_exists='append')
        else:
            print('This video has no comments...')

    def get_all_comments_of_ch(self, ch_url):
        '''指定したchの動画の全てのコメントを取得する

        Args
        ============
        ch_url : string
            取得したいchのurl
            ex. 'http://ch.nicovideo.jp/garo-project'
        '''
        ch_all = self.get_url_ch_all(ch_url)

        for c in ch_all:
            print('  ' + c[2])
            self.get_all_comments_of_thread(c[1])

    def get_all_comments_of_video_db(self, max_n_iter=1):
        '''SQLiteのvideosにある動画のコメントを全て取得する．

        Example
        ============
        videoに登録した後に以下を実行

        >>> ncrawler.get_all_comments_of_video_db()
        '''
        df = pd.read_sql('SELECT * FROM videos;', self.con)

        for n, d in df.T.to_dict().items():
            print(d['title'])
            self.get_all_comments_of_thread(d['thread'], d['title'],
                                            max_n_iter=max_n_iter)

    def initialize_csv_from_db(self, csv_path):
        '''SQLiteのvideosテーブルにある動画リストをCSVに書き出す

        出力するCSVのcrawled列は，
        * その行の動画を取得していたら1
        * そうでなければ0
        を意味する．

        Args
        ============
        csv_path : string
            CSVの出力先
        '''
        df = pd.read_sql('SELECT * FROM videos;', self.con)
        df.ix[:, 'crawled'] = int(False)
        df.to_csv(csv_path)

    def initialize_csv_from_url(self, url, csv_path='crawled.csv', max_page=1):
        '''daily rankingから取得

        `so11111111` のような形式の動画idの動画は，getflv周りで
        うまく動作しないことを確認したので，除外して取得している．

        Args
        ============
        url : string
            取得したい動画のurlを含むページのurlを指定する．
        csv_path : string, optional (default = 'crawled.csv')
            CSVの保存先

        Example
        ============
        >>> url = 'http://www.nicovideo.jp/ranking/fav/daily/all'
        >>> ncrawler.initialize_csv_from_url(url)
        '''

        df_list = []

        for page in range(1, max_page+1):
            url_page = url + ('?page={0}'.format(page))
            html = self.get_html_text(url_page)
            
            # sm111111 の形式のURLだけ抜き出す
            video_list = re.findall('"watch/(sm\d+)"[^>]+>([^<]+)<', html)

            df_temp = pd.DataFrame(video_list, columns=['thread', 'title'])
            df_list.append(df_temp)
        
        df = pd.concat(df_list, ignore_index=True)
        
        df.ix[:, 'crawled_twi'] = 0
        df.ix[:, 'crawled_nico'] = 0
        df.to_csv(csv_path)

    def get_all_comments_of_csv(self, csv_path, max_n_iter=1000):
        '''CSVにある動画のコメントを全て取得する．

        CSVのcrawled列には，クロール済みなら1,そうでなければ0が入る．
        これを使えば，取得を中断，再開することができる．

        Args
        ============
        csv_path : string
            CSVの出力先

        Example
        ============
        >>> csv_path = 'is_crawled.csv'
        >>> ncrawler.initialize(csv_path)
        >>> ncrawler.get_all_comments_of_csv(csv_path)
        '''

        df = pd.DataFrame.from_csv(csv_path)

        for n, d in df.T.to_dict().items():
            print(d['title'])
            
            # クロールされていなかった場合:
            if not d['crawled']:
                self.get_all_comments_of_thread(d['thread'], d['title'],
                                                max_n_iter=max_n_iter)
                df.ix[n, 'crawled'] = int(True)
                df.to_csv(csv_path)

    def get_all_ch_url_of_season(self, url):
        '''指定したクールのアニメのch一覧を取得して返す

        Args
        ============
        url : string
            ex. 'http://ch.nicovideo.jp/2015winter_anime'

        Example
        ============
        >>> url = 'http://ch.nicovideo.jp/2015winter_anime'
        >>> ch_list = ncrawler.get_ch_list(url)
        '''
        text = self.get_html_text(url)
        ch_list = re.findall(
            '<a href=\"(http://ch.nicovideo.jp/[^"/]+)\">\n([^\n]+)', text
        )

        return ch_list

    def get_video_url_of_ch(self, ch_url, page=1):
        '''指定したch (アニメ番組) の過去分の動画のurl一覧を取得して返す
        pageを指定して取得する

        Args
        ============
        ch_url : string
            ex. 'http://ch.nicovideo.jp/ch2590550'
        page : int (default = 1)
            動画リストのページを指定する
        '''
        text = self.get_html_text(ch_url + '/video?page=' + str(page))
        regex = '<a href="(http://www.nicovideo.jp/watch/(\d+))" title="([^"]+)"'

        return re.findall(regex, text)

    def get_all_video_url_of_ch(self, ch_url, max_page=10):
        '''指定したch (アニメ番組) の過去分の動画のurl一覧を取得して返す
        
        Args
        ============
        ch_url : string
            ex. 'http://ch.nicovideo.jp/ch2590550'
        max_page : int, optional (default=10)
            取得するページ数の最大値．
            デフォルトでは10ページ．
            20[video/page]なのでデフォルトだと最大で200話分取得する．
        '''
        video_list_all = []

        for page in range(1, max_page+1):
            video_list = self.get_video_url_of_ch(ch_url, page=page)

            if not video_list:
                break

            video_list_all.extend(video_list)

        return video_list_all

    def get_all_video_url_of_season(self, season_url):
        '''指定したクールの全てのchの過去分の動画のurl一覧を
        SQLiteに追加してから返す．

        Args
        ============
        season_url : string
            取得したいクールのアニメ一覧ページのurl
            ex. 'http://ch.nicovideo.jp/2015winter_anime'

        Example
        ============
        >>> season_url = 'http://ch.nicovideo.jp/2015winter_anime'
        >>> video_all = ncrawler.get_all_video_url_of_season(season_url)
        '''

        video_list_all = []
        for ch in self.get_all_ch_url_of_season(season_url):
            sys.stdout.flush()
            print(ch[1])

            video_list = self.get_all_video_url_of_ch(ch[0])

            video_list_all.extend(video_list)

        columns = ['url', 'thread', 'title']
        df = pd.DataFrame(video_list_all, columns=columns)

        # SQLiteに追加
        df.to_sql('videos', self.con, index=False, if_exists='append')

        return df
