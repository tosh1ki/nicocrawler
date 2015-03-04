#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'tosh1ki'
__email__ = 'tosh1ki@yahoo.co.jp'
__date__ = '2015-03-03'


from NicoCrawler import NicoCrawler


if __name__ == '__main__':

    sqlite_path = 'nico-comments.sqlite'
    csv_path = 'crawled.csv'

    ncrawler = NicoCrawler()
    ncrawler.connect_sqlite(sqlite_path)

    # 「アニメ」カテゴリのデイリーランキング上位100位の動画のうち，
    # 公式アニメで無いものを取得する
    url = 'http://www.nicovideo.jp/ranking/fav/daily/anime'
    ncrawler.initialize_csv_from_url(url, csv_path)

    ncrawler.get_all_comments_of_csv(csv_path, max_n_iter=1)
