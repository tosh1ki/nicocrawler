NicoCrawler
===========
ニコニコ動画のコメントを取得するクローラー

# Contents

## main_crawl.py
NicoCrawlerを使って実際にクロールを行うスクリプト．

Python3.4.2で作成．

## NicoCrawler.py
nicovideo.jpをクロールするためのクラスなどが入っている．

Python3.4.2で作成．

## mysetup.py
`mysetup.py` には以下の形式でnicovideo.jpのログインに使うメールアドレスとパスワードを入れておく．

```python
login_dict = {
    'mail': 'hoge@mail.com',
    'password': 'fugafuga'
}
```
# Reference

- [ニコニコ動画:GINZA](http://www.nicovideo.jp/video_top)
- [niconicoのメッセージ(コメント)サーバーのタグや送り方の説明 - 神の味噌汁青海](http://blog.goo.ne.jp/hocomodashi/e/3ef374ad09e79ed5c50f3584b3712d61)

# Author

[tosh1ki](https://github.com/tosh1ki)
