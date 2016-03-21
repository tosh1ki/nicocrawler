nicocrawler: ニコニコ動画のコメントを取得するクローラー
===========

動作環境は Python 3.5.1 :: Anaconda 2.4.1 (64-bit)

# Contents

## main_crawl.py
NicoCrawler を使って実際にクロールを行うスクリプト．

## nicocrawler/nicocrawler.py
nicovideo.jp をクロールするためのクラスなどが入っている．

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
