import dash
import dash_mantine_components as dmc
from dash import Dash, Input, Output, State, callback, dcc, html
import jwt
import json

from auth import (
    cfg,
    fetch_sp_details,
    get_connection_obo,
    get_connection_sp,
    get_user_token,
)
from sql import (
    fetch_warehouses,
    run_query,
)
from utils import create_data_table, get_icon

app = Dash(external_stylesheets=[dmc.styles.ALL])
app.title = "Databricks 認証デモ"

app.layout = dmc.MantineProvider(
    theme={
        "fontFamily": "DM Sans, sans-serif",
        "primaryColor": "lava",
        "colors": {
            "lava": [
                "#ffe9e6",
                "#ffd2cd",
                "#ffa49a",
                "#ff7264",
                "#ff4936",
                "#ff2e18",
                "#ff1e07",
                "#e40f00",
                "#cc0500",
                "#b20000",
            ]
        },
    },
    children=dmc.AppShell(
        header={"height": 60},
        padding="md",
        children=[
            dmc.AppShellHeader(
                style={"backgroundColor": "#F9F7F4"},
                children=[
                    dmc.Container(
                        children=[
                            dmc.Group(
                                justify="space-between",
                                align="center",
                                h="100%",
                                children=[
                                    dmc.Group(
                                        gap="sm",
                                        align="center",
                                        children=[
                                            html.Img(
                                                src=app.get_asset_url("logo.svg"),
                                                height=28,
                                            ),
                                            dmc.Title(
                                                "Databricks Apps 認証デモ",
                                                order=2,
                                            ),
                                        ],
                                    ),
                                    dmc.Badge(
                                        id="header-username",
                                        variant="outline",
                                        leftSection=get_icon(
                                            "material-symbols:person-outline"
                                        ),
                                    ),
                                ],
                            )
                        ],
                        fluid=False,
                        h="100%",
                        px=0,
                    )
                ],
            ),
            dmc.AppShellMain(
                style={"backgroundColor": "#F9F7F4"},
                children=dmc.Container(
                    [
                        dmc.Grid(
                            [
                                dmc.GridCol(
                                    dmc.Select(
                                        id="sql-http-path",
                                        label="SQLウェアハウスを選択",
                                        description="稼働中のSQLウェアハウスを選択してください。",
                                        data=[],
                                        value=None,
                                        required=True,
                                        style={"width": "100%"},
                                        searchable=True,
                                        nothingFoundMessage="ウェアハウスが見つかりません",
                                        leftSection=get_icon(
                                            "material-symbols:database-outline"
                                        ),
                                    ),
                                    span=6,
                                ),
                                dmc.GridCol(
                                    dmc.TextInput(
                                        id="table-name-input",
                                        label="Unity Catalog テーブル名",
                                        description="形式: カタログ.スキーマ.テーブル",
                                        placeholder="catalog.schema.table",
                                        value="ytcy_azure_east2classic_stable.auth_demo.demo_users",
                                        required=True,
                                        style={"width": "100%"},
                                        leftSection=get_icon(
                                            "material-symbols:table-outline"
                                        ),
                                    ),
                                    span=6,
                                ),
                            ],
                            mb="lg",
                            gutter="xl",
                        ),
                        dmc.Stack(
                            [
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "サービスプリンシパル (SP) 認証",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "このアプリのSP認証情報（",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_ID"
                                                ),
                                                " および ",
                                                dmc.InlineCodeHighlight(
                                                    code="DATABRICKS_CLIENT_SECRET"
                                                ),
                                                "）を使用してクエリを実行します。",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            [
                                                "サービスプリンシパル: ",
                                                html.B(id="sp-name-display"),
                                            ],
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Button(
                                            "クエリを実行 (SP)",
                                            id="run-query-sp",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:play-arrow-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-sp",
                                            children="ステータスがここに表示されます。",
                                            title="ステータス",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                        ),
                                        html.Div(
                                            create_data_table("table-output-sp"),
                                            id="table-container-sp",
                                            style={"display": "none"},
                                        ),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-sp",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                                dmc.Paper(
                                    [
                                        dmc.Title(
                                            "ユーザー代理認証 (OBO)",
                                            order=3,
                                            mb="md",
                                        ),
                                        dmc.Text(
                                            [
                                                "アクセスするユーザーの認証情報（",
                                                dmc.InlineCodeHighlight(
                                                    code="X-Forwarded-Access-Token"
                                                ),
                                                " ヘッダー）を使用してクエリを実行します。",
                                            ],
                                            size="sm",
                                            mb="xs",
                                        ),
                                        dmc.Text(
                                            id="obo-username",
                                            size="sm",
                                            mb="md",
                                        ),
                                        dmc.Alert(
                                            id="obo-token-status",
                                            title="OBO ステータス",
                                            color="blue",
                                            mb="md",
                                            radius="sm",
                                        ),
                                        html.Div(
                                            id="accordion-container",
                                            children=dmc.Accordion(
                                                children=[
                                                    dmc.AccordionItem(
                                                        [
                                                            dmc.AccordionControl(
                                                                "アクセストークンの詳細を表示",
                                                                icon=get_icon("material-symbols:key-outline"),
                                                            ),
                                                            dmc.AccordionPanel(
                                                                [
                                                                    dmc.Stack(
                                                                        [
                                                                            dmc.Text("生JWTトークン:", size="sm", fw=500, mb="xs"),
                                                                            dmc.ScrollArea(
                                                                                dmc.Code(
                                                                                    id="jwt-raw-token",
                                                                                    children="トークンが利用可能になるとここに表示されます",
                                                                                    block=True,
                                                                                    style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
                                                                                ),
                                                                                h=100,
                                                                                type="auto",
                                                                            ),
                                                                            dmc.Divider(my="md"),
                                                                            dmc.Text("デコードされたJWTペイロード:", size="sm", fw=500, mb="xs"),
                                                                            dmc.ScrollArea(
                                                                                dmc.Code(
                                                                                    id="jwt-decoded",
                                                                                    children="デコードされたトークンがここに表示されます",
                                                                                    block=True,
                                                                                    style={"whiteSpace": "pre"},
                                                                                ),
                                                                                h=200,
                                                                                type="auto",
                                                                            ),
                                                                            dmc.Divider(my="md"),
                                                                            dmc.Text("スコープ一覧:", size="sm", fw=500, mb="xs"),
                                                                            html.Div(id="jwt-scopes-list"),
                                                                        ],
                                                                        gap="sm",
                                                                    )
                                                                ]
                                                            ),
                                                        ],
                                                        value="token-details",
                                                    )
                                                ],
                                                mb="md",
                                            ),
                                        ),
                                        dmc.Button(
                                            "クエリを実行 (OBO)",
                                            id="run-query-obo",
                                            variant="outline",
                                            leftSection=get_icon(
                                                "material-symbols:play-arrow-outline"
                                            ),
                                            mb="md",
                                            loading=False,
                                            loaderProps={
                                                "variant": "dots",
                                                "size": "sm",
                                            },
                                        ),
                                        dmc.Alert(
                                            id="alert-obo",
                                            children="ステータスがここに表示されます。",
                                            title="ステータス",
                                            color="gray",
                                            withCloseButton=True,
                                            hide=True,
                                            radius="sm",
                                            mt="md",
                                        ),
                                        html.Div(
                                            create_data_table("table-output-obo"),
                                            id="table-container-obo",
                                            style={"display": "none"},
                                        ),
                                        dmc.LoadingOverlay(
                                            id="loading-overlay-obo",
                                            visible=False,
                                            loaderProps={"variant": "dots"},
                                        ),
                                    ],
                                    shadow="sm",
                                    p="lg",
                                    radius="md",
                                    withBorder=True,
                                    style={"position": "relative"},
                                ),
                            ],
                            gap="xl",
                        ),
                        html.Div(id="initial-load-trigger", style={"display": "none"}),
                        dcc.Store(id="obo-token-store"),
                    ],
                    fluid=False,
                    p="0",
                ),
            ),
        ],
    ),
)


@callback(
    [
        Output("header-username", "children"),
        Output("obo-token-status", "children"),
        Output("obo-token-status", "color"),
        Output("obo-token-status", "title"),
        Output("run-query-obo", "disabled"),
        Output("obo-token-store", "data"),
        Output("obo-username", "children"),
        Output("sql-http-path", "data"),
        Output("sql-http-path", "value"),
        Output("sp-name-display", "children"),
        Output("jwt-raw-token", "children"),
        Output("jwt-decoded", "children"),
        Output("jwt-scopes-list", "children"),
        Output("accordion-container", "style"),
    ],
    Input("initial-load-trigger", "children"),
)
def update_header_and_warehouses(_):
    wh_options, wh_value = fetch_warehouses()
    sp_name = fetch_sp_details()

    header_username_display = ["ユーザー: ", dmc.Code("不明")]
    obo_status_msg = "OBOステータスを確認中..."
    obo_color = "gray"
    obo_title = "確認中..."
    obo_disabled = True
    has_token = False
    obo_username = ["現在のユーザー: ", html.B("不明")]
    jwt_raw = "トークンがありません"
    jwt_decoded = "デコードするトークンがありません"
    jwt_scopes_list = dmc.Text("スコープがありません", size="sm", c="dimmed")
    accordion_style = {"display": "none"}

    try:
        from flask import request

        headers = dict(request.headers)
        username = headers.get("X-Forwarded-Preferred-Username")
        obo_token = headers.get("X-Forwarded-Access-Token")

        header_username_display = username if username else "利用不可"
        obo_username = [
            "現在のユーザー: ",
            html.B(username if username else "利用不可"),
        ]

        has_token = bool(obo_token)
        has_sql_scope = False

        if has_token:
            accordion_style = {"display": "block"}
            jwt_raw = obo_token

            try:
                decoded_token = jwt.decode(obo_token, options={"verify_signature": False})
                jwt_decoded = json.dumps(decoded_token, indent=2)

                scopes = decoded_token.get("scope", "").split()
                has_sql_scope = any('sql' in scope.lower() for scope in scopes)

                if scopes:
                    jwt_scopes_list = dmc.List(
                        [dmc.ListItem(dmc.Code(scope)) for scope in scopes],
                        size="sm",
                        spacing="xs",
                    )
                else:
                    jwt_scopes_list = dmc.Text("トークンにスコープが見つかりません", size="sm", c="dimmed")

            except Exception as e:
                jwt_decoded = f"JWTデコードエラー: {str(e)}"
                jwt_scopes_list = dmc.Text("スコープ解析エラー", size="sm", c="red")

            if has_sql_scope:
                obo_status_msg = [
                    dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                    " にSQLスコープが含まれています。OBOは正しく設定されています。",
                ]
                obo_color = "green"
                obo_title = "OBO設定済み"
                obo_disabled = False
            else:
                obo_status_msg = [
                    dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                    " が見つかりましたが、SQLスコープがありません。OBOを使用するにはSQLスコープを有効にしてください。",
                ]
                obo_color = "orange"
                obo_title = "SQLスコープ未設定"
                obo_disabled = True

        else:
            obo_status_msg = [
                dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                " ヘッダーが見つかりません。OBOを使用するにはこのヘッダーが必要です。アプリのOBOを有効にしてください。",
            ]
            obo_color = "orange"
            obo_title = "OBO利用不可"
            obo_disabled = True

    except Exception:
        header_username_display = ["ユーザー: ", dmc.Code("エラー")]
        obo_status_msg = "OBOステータスの読み込みに失敗しました。"
        obo_color = "red"
        obo_title = "ヘッダー読み込みエラー"
        obo_disabled = True
        has_token = False

    return (
        header_username_display,
        obo_status_msg,
        obo_color,
        obo_title,
        obo_disabled,
        {"has_token": has_token},
        obo_username,
        wh_options,
        wh_value,
        sp_name,
        jwt_raw,
        jwt_decoded,
        jwt_scopes_list,
        accordion_style,
    )


@callback(
    [
        Output("table-output-sp", "data"),
        Output("table-output-sp", "columns"),
        Output("table-output-sp", "tooltip_data"),
        Output("alert-sp", "children"),
        Output("alert-sp", "color"),
        Output("alert-sp", "hide"),
        Output("alert-sp", "title"),
        Output("table-container-sp", "style"),
        Output("loading-overlay-sp", "visible"),
        Output("run-query-sp", "loading"),
    ],
    Input("run-query-sp", "n_clicks"),
    State("sql-http-path", "value"),
    State("table-name-input", "value"),
    running=[
        (Output("run-query-sp", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def run_sp_query_callback(n_clicks, http_path, table_name):
    container_style = {"display": "none"}
    loading_visible = False

    if not n_clicks or not http_path or not table_name:
        return dash.no_update + (False, False)

    if not cfg:
        return (
            [],
            [],
            [],
            [
                "エラー: Databricks SDKが設定されていません。",
                dmc.InlineCodeHighlight(code="DATABRICKS_HOST"),
                " などの環境変数を確認してください。",
            ],
            "red",
            False,
            "設定エラー",
            container_style,
            False,
            False,
        )

    loading_visible = True
    alert_hide = False

    try:
        conn = get_connection_sp(http_path)
        df = run_query(table_name, conn)
        conn.close()
        loading_visible = False

        if not df.empty:
            data = df.to_dict("records")
            columns = [{"name": i, "id": i} for i in df.columns]
            tooltips = [
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in data
            ]
            alert_msg = [
                "成功！サービスプリンシパルの権限で ",
                dmc.Code(f"{table_name}"),
                " から ",
                html.B(f"{len(df)}"),
                " 件のデータを取得しました。",
            ]
            alert_color = "green"
            alert_title = "成功"
            container_style = {"display": "block"}
            return (
                data,
                columns,
                tooltips,
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )
        else:
            alert_msg = [
                "サービスプリンシパルでクエリは成功しましたが、",
                dmc.Code(f"'{table_name}'"),
                " からデータが返されませんでした。",
            ]
            alert_color = "yellow"
            alert_title = "データなし"
            return (
                [],
                [],
                [],
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )

    except Exception as e:
        loading_visible = False
        alert_msg = ["サービスプリンシパルでのクエリエラー: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "エラー"
        return (
            [],
            [],
            [],
            alert_msg,
            alert_color,
            alert_hide,
            alert_title,
            container_style,
            loading_visible,
            False,
        )


@callback(
    [
        Output("table-output-obo", "data"),
        Output("table-output-obo", "columns"),
        Output("table-output-obo", "tooltip_data"),
        Output("alert-obo", "children"),
        Output("alert-obo", "color"),
        Output("alert-obo", "hide"),
        Output("alert-obo", "title"),
        Output("table-container-obo", "style"),
        Output("loading-overlay-obo", "visible"),
        Output("run-query-obo", "loading"),
    ],
    Input("run-query-obo", "n_clicks"),
    State("sql-http-path", "value"),
    State("table-name-input", "value"),
    running=[
        (Output("run-query-obo", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def run_obo_query_callback(n_clicks, http_path, table_name):
    container_style = {"display": "none"}
    loading_visible = False

    if not n_clicks or not http_path or not table_name:
        return dash.no_update + (False, False)

    if not cfg:
        return (
            [],
            [],
            [],
            [
                "エラー: Databricks SDKが設定されていません。",
                dmc.InlineCodeHighlight(code="DATABRICKS_HOST"),
                " などの環境変数を確認してください。",
            ],
            "red",
            False,
            "設定エラー",
            container_style,
            False,
            False,
        )

    loading_visible = True
    alert_hide = False

    try:
        user_token = get_user_token()
        if not user_token:
            alert_msg = [
                "エラー: ",
                dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                " がリクエストヘッダーに見つかりません。OBOクエリを実行できません。アプリのOBOが有効になっているか確認してください。",
            ]
            alert_color = "red"
            alert_title = "OBOトークン未検出"
            loading_visible = False
            return (
                [],
                [],
                [],
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )

        conn = get_connection_obo(http_path, user_token)
        df = run_query(table_name, conn)
        conn.close()
        loading_visible = False

        if not df.empty:
            data = df.to_dict("records")
            columns = [{"name": i, "id": i} for i in df.columns]
            tooltips = [
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in data
            ]
            alert_msg = [
                "成功！OBO認証で ",
                dmc.Code(f"{table_name}"),
                " から ",
                html.B(f"{len(df)}"),
                " 件のデータを取得しました。",
            ]
            alert_color = "green"
            alert_title = "成功"
            container_style = {"display": "block"}
            return (
                data,
                columns,
                tooltips,
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )
        else:
            alert_msg = [
                "OBOクエリは成功しましたが、",
                dmc.Code(f"'{table_name}'"),
                " からデータが返されませんでした。",
            ]
            alert_color = "yellow"
            alert_title = "データなし"
            return (
                [],
                [],
                [],
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )

    except Exception as e:
        loading_visible = False
        alert_msg_base = ["OBOでのクエリエラー: ", dmc.Code(str(e))]
        alert_color = "red"
        alert_title = "エラー"
        if (
            "PERMISSION_DENIED" in str(e).upper()
            or "DOES NOT HAVE PRIVILEGE" in str(e).upper()
        ):
            alert_msg = alert_msg_base + [
                " | ユーザーがテーブルへのSELECT権限およびウェアハウス/カタログ/スキーマへのUSE権限を持っているか確認してください。"
            ]
        elif "OBO token not found" in str(e):
            alert_msg = [
                "エラー: OBOトークン（",
                dmc.InlineCodeHighlight(code="X-Forwarded-Access-Token"),
                "）が見つかりません。このアプリのOBOが有効になっており、Databricks経由でアクセスしているか確認してください。",
            ]
        else:
            alert_msg = alert_msg_base

        return (
            [],
            [],
            [],
            alert_msg,
            alert_color,
            alert_hide,
            alert_title,
            container_style,
            loading_visible,
            False,
        )


if __name__ == "__main__":
    app.run()
