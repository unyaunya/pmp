# PMP

----
## このツールは何ですか？
    Ganttチャートを作るツールです。

![サンプル](../../wiki/images/sample.png)
![サンプル](../../wiki/images/_blob/sample.png)

----
## 動作環境
    Python+PyQtが使えれば動くハズ。

### OS

* Windows

    Windows7(32,64bitとも)でしかまともに動かしてません。

* Mac

    MountainLionで動かしたことあります。

* Linux

    動かしたことありません。

### Python

    PyScripterが3.4に対応してないので、3.3で開発していますが、おそらく3.4でも動くと思います。

    ここから入手できます。
    http://www.python.jp/

### PyQt
    4.8.6で動かしてます。

    次のバージョンは使ったことがあります。

　　Python3.3-64bit用：
　　　　PyQt4-4.10.4-gpl-Py3.3-Qt4.8.6-x64.exe
　　Python3.3-32bit用：
　　　　PyQt4-4.11.3-gpl-Py3.3-Qt4.8.6-x32.exe
　　　　PyQt4-4.11.3-gpl-Py3.4-Qt4.8.6-x32.exe

    バイナリは次のサイトから入手できます。

	http://www.riverbankcomputing.co.uk/software/pyqt/download


## 動かし方

    > git clone http://gitserver:port/git/wata/pmp.git
    > python pmp\pmp.pyw

## その他

### 使えない機能

　　[サーバを開く]メニューとか使えません。

    flaskの勉強がてら、サーバ機能を作りかけてるところです。
　　誰もアクセスしないでしょうから、masterブランチに作りかけで動かない機能が入ってます。

### 機能追加

　　次のような機能を追加したいのですが、時間がとれません。
    ・イベントの登録/表示
　　・タスク間の依存関係の設定と表示
　　・連続する複数タスクを１行にまとめて表示

### ライセンス
    PyQt は GPLらしい。
    Pythonは PSFライセンス
