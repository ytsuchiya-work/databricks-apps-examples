# Databricks Apps: サービスプリンシパルとOBO認証デモ

このサンプルアプリは、[Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html) 上でUnity Catalog経由のDatabricks SQLウェアハウスに対してクエリを実行する際の、2種類の認証方式を比較・デモするアプリケーションです。

## 認証方式の比較

1. **サービスプリンシパル (SP) 認証**  
   アプリ自身のSP認証情報（`DATABRICKS_CLIENT_ID` および `DATABRICKS_CLIENT_SECRET`）を使用してクエリを実行します。列マスキングポリシーが適用される場合、SPにはマスクされたデータが返されます。

2. **ユーザー代理認証 (OBO: On-Behalf-Of)**  
   Databricksが提供する `X-Forwarded-Access-Token` ヘッダーを通じて、アクセスするユーザーのIDでクエリを実行します。ユーザーが適切な権限を持っている場合、列マスキングが適用されず実データが返されます。

## デモデータについて

デモテーブル `ytcy_azure_east2classic_stable.auth_demo.demo_users` には、日本語の社員情報（氏名・メールアドレス・部署・役職・入社年度・給与）が格納されています。

**列マスキングポリシー**: `メールアドレス` 列にはサービスプリンシパル用のマスキングポリシーが設定されています。
- **SP認証でクエリを実行**すると、メールアドレスがマスクされた状態で返されます（例: `ta****@****.co.jp`）。
- **OBO認証でクエリを実行**すると、ログインユーザーの権限でアクセスするため、実際のメールアドレスが表示されます。

![Databricks Apps: サービスプリンシパルとOBO認証デモ](assets/screenshot.png "Databricks Apps: サービスプリンシパルとOBO認証デモ")

## Databricks Appとしてデプロイする手順

1. このGitHubリポジトリをDatabricksワークスペースの[Gitフォルダ](https://docs.databricks.com/en/repos/index.html)として読み込みます。
2. Databricksワークスペースで **コンピュート** → **アプリ** に移動します。
3. **アプリの作成** を選択します。
4. **開始方法を選択** で **カスタム** を選び、**次へ** をクリックします。
5. アプリの名前を入力します。
6. **詳細設定** で、**アプリがDatabricksのSQLリソースを実行・管理できるようにする** にチェックを入れてSQLスコープを有効化します。
7. **アプリの作成** をクリックします。
8. アプリのコンピュートが起動したら **デプロイ** を選択します。
9. Gitフォルダに移動し、`auth-demo` フォルダを選択します。
10. **デプロイ** をクリックします。

## ローカルで実行する手順

1. リポジトリをクローンして `auth-demo` フォルダに移動します:
   ```bash
   git clone https://github.com/ytsuchiya-work/databricks-apps-examples.git
   cd databricks-apps-examples/auth-demo
   ```
2. [uv](https://docs.astral.sh/uv/) をインストールします（未インストールの場合）。
3. [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html) をインストールし、[OAuth U2M](https://docs.databricks.com/en/dev-tools/auth/oauth-u2m.html) でワークスペースに認証します:
   ```bash
   databricks auth login --host https://adb-7405605463330453.13.azuredatabricks.net/
   ```
4. アプリを起動します（uvが自動的に仮想環境を作成して依存パッケージをインストールします）:
   ```bash
   uv run python app.py
   ```

> [!NOTE]
>
> - ローカル実行時は `X-Forwarded-Access-Token` ヘッダーが存在しないため、OBO認証は動作しません。
> - SP認証セクションでは、CLIで設定したユーザー認証情報が使用されます。

---

&copy; 2025 Databricks, Inc. All rights reserved. The source in this repository is provided subject to the Databricks License [https://databricks.com/db-license-source].

| ライブラリ               | 説明                                               | ライセンス    | ソース                                              |
| ------------------------ | -------------------------------------------------- | ------------ | --------------------------------------------------- |
| dash                     | 分析用Webアプリケーションフレームワーク             | MIT          | https://github.com/plotly/dash                      |
| dash-iconify             | Dashアプリ向けアイコンコンポーネント               | MIT          | https://github.com/snehilvj/dash-iconify            |
| dash_mantine_components  | DashのManineコンポーネント                         | MIT          | https://github.com/snehilvj/dash-mantine-components |
| databricks-sdk           | Databricks Python SDK                              | Apache 2.0   | https://github.com/databricks/databricks-sdk-py     |
| databricks-sql-connector | Databricks SQL Connector for Python                | Apache 2.0   | https://github.com/databricks/databricks-sql-python |
| Flask                    | 軽量WSGIウェブアプリケーションフレームワーク       | BSD 3-Clause | https://github.com/pallets/flask                    |
| pandas                   | データ分析・操作ライブラリ                         | BSD 3-Clause | https://github.com/pandas-dev/pandas                |
| pyarrow                  | Apache Arrow Python ライブラリ                     | Apache 2.0   | https://github.com/apache/arrow/tree/main/python    |

---

## 質問・問題について

エラーが発生した場合はこのリポジトリにIssueを作成してください。
