# 🀐 Tenhou Log Command Line Utility 🀐

## 🀦 What is this? / このリポジトリについて

Tenhou Log Utils is command line tools, written in Python, to analyze game log of online mahjong Tenhou.net.

天鳳ログユーティリティはオンライン麻雀サイト tenhou.net のゲームログを解析するためのコマンドラインツールです。

Tenhou Log Utils

以下のことができます。

 - Pick up IDs of the games you played form Flash player cache.

    ローカルディスクに保存されている Flash Player のキャッシュから、今までにプレイした卓のログ ID をリストアップ。

 - Download `mjlog` file from tenhou.net.

    `mjlog` 形式ファイルをダウンロード。

 - View `mjlog` file in console.

    `mjlog` 形式ファイルの中身をコンソールに表示。


## 🀧 Usage / 使い方

Once it's installed, you should be able to use command `tlu` (stands for Tenhou Log Utilities).   
You can use `--help` to see how to use.


インストールが完了すると、`tlu` コマンド (`T`enhou `L`og `U`tilities の略です。) が使えるはずです。   
`--help` オプションで使い方が表示されます。（英語のみ）

```bash
tlu --help
```

This will print message like the following.

以下のようなメッセージが表示されます。

```
usage: tlu [-h] {view,list,download} ...

Utility for tenhou.net log files.

positional arguments:
  {view,list,download}

optional arguments:
  -h, --help            show this help message and exit
```


### 🀇 List up your game history. / ゲーム履歴を表示

Using `list` sub command you can list up the information on your play history.

`list` サブコマンドを使うとローカルディスクに保存されたゲームの履歴を表示できます。

```bash
tlu list
```

```
/Users/moto/Library/Preferences/Macromedia/Flash Player/#SharedObjects/XRF2TRTU/mjv.jp/mjinfo.sol:
  file: 2017060503gm-0041-0000-da7fdf26
  un0: jesse
  un1: たろ＿
  un2: Yakkuru
  un3: みふき
  oya: 2
  type: 65
  sc: 143,-26.0,606,71.0,346,15.0,-95,-60.0

/Users/moto/Library/Application Support/Google/Chrome/Default/Pepper Data/Shockwave Flash/WritableRoot/#SharedObjects/YSXJKZMQ/mjv.jp/mjinfo.sol:
  file: 2017052413gm-0009-0000-2c57e05a
  un0: jesse
  un1: NoName
  un2: toru.ysk
  un3: んほおお
  oya: 1
  type: 9
  sc: 340,14.0,131,-27.0,80,-42.0,449,55.0
  
  ...
  
```

You can use `--id-only` option to only show log IDs. You need these IDs to download play log from tenhou.net.

`--id-only` オプションを使うことで ID のみを表示することができます。これらを使って tenhou.net からゲームのログをダウンロードするのに必要になります。

```bash
tlu list --id-only
```

```
2017060503gm-0041-0000-da7fdf26
2017052413gm-0009-0000-2c57e05a
2017052414gm-0009-0000-b0b25432
2017052514gm-0009-0000-df77ea6e
2017052514gm-0009-0000-e9f23937
2017052514gm-0009-0000-69a2af52
2017052515gm-0001-0000-42e80591
2017052612gm-0009-0000-815ed634
2017053113gm-0009-0000-6a4d36ba
2017053114gm-0009-0000-2294be5f
2017060213gm-0009-0000-a0c95a8f
2017060314gm-0009-0000-3b2aa4ca
2017060409gm-0001-0000-87fec10c
2017060409gm-0001-0000-f9ade363
2017060413gm-0009-0000-1508d27d
```


### 🀈 Download mjlog file / mjlog ファイルのダウンロード

With `download` sub command, you can download play log (`mjlog` file). You need the log ID of the game you want to download.

`download` サブコマンドを使ってゲームのプレイログ（`mjlog` 形式）をダウンロードすることができます。ダウンロードしたいゲームの ID が必要になります。

Example)

The following command will download the play log with ID `2017060314gm-0009-0000-3b2aa4ca` to `2017060314gm-0009-0000-3b2aa4ca.mjlog` in the local storage.

以下のコマンドは ID `2017060314gm-0009-0000-3b2aa4ca` のゲームログを `2017060314gm-0009-0000-3b2aa4ca.mjlog` にダウンロードします。

```bash
tlu download 2017060314gm-0009-0000-3b2aa4ca 2017060314gm-0009-0000-3b2aa4ca.mjlog
```


### 🀉 View downloaded mjlog file.

You can use `view` command to see the content of a `mjlog` file.

`view` コマンドを使って `mjlog` ファイルの中身を表示できます。

```bash
tlu view 2017060314gm-0009-0000-3b2aa4ca.mjlog
```

```
Lobby 0:
    test: False
    red: True
    kui: True
    ton-nan: True
    sanma: False
    tokujou: False
    soku: False
    joukyu: False
Players:
  Index: Dan,     Rate, Sex, Name
      0:   7,  1601.97,   M, AlyBBBMe
      1:   3,  1558.81,   M, jesse
      2:   0,  1484.34,   M, すっぽん3号
      3:   0,  1500.00,   M, NoName
Dealer: 0
========================================
Initial Game State:
  Round: 0
  Combo: 0
  Reach: 0
  Dice 1: 3
  Dice 2: 3
  Dora Indicator: 🀅 0
  Initial Scores:
      0:  25000
      1:  25000
      2:  25000
      3:  25000
  Dealer: 0
  Initial Hands:
      0: 🀔 2 🀗 2 🀘 1 🀜 0 🀞 3 🀡 0 🀊 0 🀊 3 🀎 3 🀏 3 🀀 3 🀃 1 🀃 3
      1: 🀒 2 🀒 3 🀖 3 🀗 3 🀝 2 🀟 2 🀟 3 🀠 3 🀋 3 🀌 1 🀍 0 🀀 2 🀆 3
      2: 🀒 0 🀔 0 🀔 3 🀖 2 🀗 1 🀙 1 🀛 2 🀜 3 🀠 0 🀊 1 🀋 0 🀍 3 🀂 1
      3: 🀓 3 🀖 1 🀙 3 🀚 1 🀛 0 🀛 3 🀈 1 🀋 1 🀌 0 🀍 2 🀎 2 🀁 1 🀆 1
Player 0: Draw    🀅 2
Player 0: Discard 🀅 2
Player 1: Draw    🀁 0

...


Player 3: ChanKan from player 1: 🀂 2🀂 1🀂 0🀂 3
Player 3: Draw    🀌 2
New Dora Indicator: 🀄 1
Player 3: Discard 🀍 1
Player 0: Chi from player 3: 🀍 1🀌 3🀎 0
Player 0: Discard 🀉 3
Player 1: Draw    🀌 1
Player 1: Discard 🀌 1
Player 2: Draw    🀌 0
Player 2: Discard 🀌 0
Player 3: Chi from player 2: 🀌 0🀋 0🀍 0
Player 3: Discard 🀕 3
Player 0: Draw    🀍 3
Player 0: Discard 🀍 3
Player 1: Draw    🀜 0
Player 1 wins.
  Tsumo.
  Hand: 🀙 2 🀙 3 🀚 2 🀚 3 🀛 2 🀛 3 🀜 0 🀝 1 🀞 3 🀟 0 🀟 1 🀟 3 🀠 3 🀡 3
  Machi: 🀜 0
  Dora Indicator: 🀋 1 🀄 1
  Ura Dora: 🀓 3 🀈 0
  Yaku:
      Reach                ( 1):  1 [Han]
      Tsumo                ( 0):  1 [Han]
      Pin-fu               ( 7):  1 [Han]
      Ii-pei-ko            ( 9):  1 [Han]
      Ikki-tsuukan         (24):  2 [Han]
      Chin-itsu            (35):  6 [Han]
      Ura-dora             (53):  0 [Han]
  Fu: 20
  Score: 36000
    - Sanbaiman
  Ten-bou:
    Combo: 0
    Riichi: 1
  Scores:
     35700:  -120
      6800:   370
     55700:  -120
       800:  -120
  Final scores:
     23700: -16.0
     43800:  53.0
     43700:  24.0
    -11200: -61.0

```


## 🀨 Installation / インストール

### 🀙 Normal Installation / 通常インストール

Use the following command to install TLU.

以下のコマンドでインストールできます。

```bash
pip install git+git://github.com/mthrok/tenhou-log-utils.git
```

### 🀚 Development Installation / 開発版インストール

If you want to modify the command line, you can install in editable mode.

#### 1. Clone the repository / リポジトリをクローン

```bash
git clone http://github.com/mthrok/tenhou-log-utils
cd tenhou-log-utils
```

#### 2. Install with `-e` option. / `-e` オプション付きでインストール

```bash
pip install -e .
```

This will install the utility from the local repo, and you can change the behavior by modifying the content of `tenhou_log_utils` directory.

これでコマンドがクローンしたレポジトリを参照するようにインストールされます。`tenhou_log_utils` の中のスクリプトを編集することで、コマンドの挙動を変更できます。


## 🀩 Bug Report / バグの報告

Please file a bug report at [issues page](https://github.com/mthrok/tenhou-log-utils/issues). Ideas and suggestions are also welcome.

バグを発見した場合は [こちら](https://github.com/mthrok/tenhou-log-utils/issues)に報告をお願いします。機能改善要望もどうぞ。日本語でおk。
