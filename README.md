# Houdini Help Editor
HoudiniのHDAにヘルプを追加、編集する為のスクリプトです。

![Help Editor.gif](https://dl.dropboxusercontent.com/s/fiilusmm4sk5jnq/HelpEditor.gif?dl=0)

このツールとHDAにヘルプを持たせる方法の紹介は下記ページをご覧ください。

[HDAにヘルプを付ける方法(Pythonスクリプトのおまけ付き)](https://qiita.com/d658t/private/1737cb4e820b45f28723)

# インストール
**Clone or download > Download ZIP**からZIPファイルをダウンロードしてください。

解凍したフォルダ内の**python2.7libs**フォルダ、**OPmenu.xml**を環境変数**HOUDINI_PATH**が通ってる場所へコピーしてください。

![Install](https://dl.dropboxusercontent.com/s/f48fax5jhdex5kv/Install.jpg?dl=0)

# スクリプトの起動
Houdiniを起動し、ヘルプを追加、編集したいノードの上で**右クリック > Edit Node Help**をクリックします。

# 機能
- 起動時に選択したノードのノードタイプ、パラメータを読み込み、ヘルプのひな形を表示します。

- 起動時にHDAのインストールディレクトリからHelpテキストファイルとカスタムサンプルを検索し、存在すればその値を読み込んでUIに反映させます。標準ノードのヘルプも読み込めますが、編集は出来ません。

- 概要、ノードの説明、パラメータの説明、カスタムサンプルの説明を編集することが出来ます。

- カスタムサンプルのLoadボタンを押すとカスタムサンプルが読み込まれます。Launchはカスタムサンプルが読み込まれた状態で新しいHoudiniが起動します。

- Show Help Textボタンを押すと現在のマークアップを別ウィンドウで表示します。

- Export Help Textボタンを押すと適切な場所にヘルプテキストファイルを書き出し、その後、ヘルプブラウザが起動します。

- ウィンドウはタブウィンドウになっているので、複数のノードのヘルプをまとめて、表示、編集することが出来ます。

![Tab Window](https://dl.dropboxusercontent.com/s/2sxqgx1mck2z602/Tab.jpg?dl=0)

- 概要、ノードの説明、パラメータの説明欄はリサイズ出来るようになっています。

![Resize](https://dl.dropboxusercontent.com/s/nsrf7m78mictwqn/Resize.gif?dl=0)
