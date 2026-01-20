# CursorとGitHub連携ガイド

## 方法1: Cursorの統合機能を使用（推奨）

### ステップ1: CursorでGitHubアカウントを連携

1. Cursorを開く
2. 左下の歯車アイコン（⚙️）をクリックして設定を開く
3. 「Accounts」または「GitHub」セクションを探す
4. 「Sign in with GitHub」をクリック
5. ブラウザが開くので、GitHubアカウントでログインして認証を完了

### ステップ2: Gitリポジトリの初期化

ターミナルで以下のコマンドを実行：

```bash
# Gitリポジトリを初期化
git init

# 現在のファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit"
```

### ステップ3: GitHubでリポジトリを作成

1. GitHub.comにアクセス
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `meeting-minutes-summarization`）
4. 「Create repository」をクリック
5. 表示されるURLをコピー（例: `https://github.com/yourusername/meeting-minutes-summarization.git`）

### ステップ4: リモートリポジトリを追加

ターミナルで以下のコマンドを実行（URLは実際のリポジトリURLに置き換えてください）：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/yourusername/your-repo-name.git

# ブランチ名をmainに設定（必要に応じて）
git branch -M main

# GitHubにプッシュ
git push -u origin main
```

## 方法2: GitHub CLIを使用

### ステップ1: GitHub CLIのインストール

1. https://cli.github.com/ からGitHub CLIをダウンロード・インストール
2. インストール後、ターミナルで認証：

```bash
gh auth login
```

### ステップ2: リポジトリの作成とプッシュ

```bash
# Gitリポジトリを初期化
git init

# ファイルを追加
git add .

# 初回コミット
git commit -m "Initial commit"

# GitHubにリポジトリを作成してプッシュ
gh repo create --source=. --public --push
```

## 方法3: Personal Access Tokenを使用

### ステップ1: GitHubでPersonal Access Tokenを作成

1. GitHub.comにログイン
2. 右上のプロフィール画像 → 「Settings」
3. 左メニューの「Developer settings」
4. 「Personal access tokens」→「Tokens (classic)」
5. 「Generate new token (classic)」をクリック
6. 必要な権限を選択（最低限 `repo` にチェック）
7. 「Generate token」をクリック
8. **トークンをコピーして保存**（後で表示されません）

### ステップ2: Gitで認証情報を設定

```bash
# Gitリポジトリを初期化
git init

# ファイルを追加
git add .

# 初回コミット
git commit -m "Initial commit"

# リモートリポジトリを追加
git remote add origin https://github.com/yourusername/your-repo-name.git

# プッシュ時にトークンを使用
# ユーザー名: あなたのGitHubユーザー名
# パスワード: Personal Access Token
git push -u origin main
```

## CursorでのGit操作

Cursorでは以下の方法でGit操作が可能です：

1. **ソース管理パネル**: 左サイドバーの「Source Control」アイコン（分岐マーク）をクリック
2. **コミット**: 変更をステージングしてコミットメッセージを入力
3. **プッシュ/プル**: 右上の同期アイコンまたは「...」メニューから実行
4. **ブランチ管理**: 左下のブランチ名をクリックして切り替え

## トラブルシューティング

### 認証エラーが発生する場合

```bash
# Gitの認証情報を確認
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 認証情報をクリア（必要に応じて）
git credential-manager-core erase
```

### リモートリポジトリを変更する場合

```bash
# 現在のリモートを確認
git remote -v

# リモートを削除
git remote remove origin

# 新しいリモートを追加
git remote add origin https://github.com/yourusername/new-repo.git
```
