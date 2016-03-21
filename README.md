nicocrawler: ニコニコ動画のコメントを取得するクローラー
===========

動作環境は Python 3.5.1 :: Anaconda 2.4.1 (64-bit)

```sh
./crawl_comments.py --url "http://ch.nicovideo.jp/2016winter_anime" --mail $LOGINMAIL --pass $LOGINPASS --sqlite /path/to/niconico_comments.sqlite3
```

# Reference

- [ニコニコ動画:GINZA](http://www.nicovideo.jp/video_top)
- (リンク切れ)[niconicoのメッセージ(コメント)サーバーのタグや送り方の説明 - 神の味噌汁青海](http://blog.goo.ne.jp/hocomodashi/e/3ef374ad09e79ed5c50f3584b3712d61)
