#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'tosh1ki'
__email__ = 'tosh1ki@yahoo.co.jp'
__date__ = '2015-03-03'


import argparse

from NicoCrawler import NicoCrawler


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sqlite_path',
                        default='comments.sqlite3',
                        help='クロールしたデータを保存するSQLiteの場所')
    parser.add_argument('-c', '--csv_path',
                        default='crawled.csv',
                        help='クロールする予定のURLを集めたCSV')
    args = parser.parse_args()
    sqlite_path = args.sqlite_path
    csv_path = args.csv_path

    ncrawler = NicoCrawler()
    ncrawler.connect_sqlite(sqlite_path)

    url = 'http://ch.nicovideo.jp/2015spring_anime'
    df = ncrawler.get_all_video_url_of_season(url)
    ncrawler.initialize_csv_from_db('crawled.csv')

    # # デイリーランキング1~300位の動画を取得する
    # url = 'http://www.nicovideo.jp/ranking/fav/daily/all'
    # ncrawler.initialize_csv_from_url(url, csv_path, max_page=3)

    ncrawler.get_all_comments_of_csv(csv_path, max_n_iter=1)
