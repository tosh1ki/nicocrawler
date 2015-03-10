#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'tosh1ki'
__email__ = 'tosh1ki@yahoo.co.jp'
__date__ = '2015-03-03'


from NicoCrawler import NicoCrawler


if __name__ == '__main__':

    sqlite_path = '/mnt/subdisk/data/deanony/nico-all.sqlite'
    csv_path = 'crawled.csv'

    ncrawler = NicoCrawler()
    ncrawler.connect_sqlite(sqlite_path)

    # デイリーランキング1~300位の動画を取得する
    url = 'http://www.nicovideo.jp/ranking/fav/daily/all'
    ncrawler.initialize_csv_from_url(url, csv_path, max_page=3)

    ncrawler.get_all_comments_of_csv(csv_path, max_n_iter=1)
