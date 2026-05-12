import os
import json
import requests
from datetime import datetime, date

import dash
from dash import Dash, dcc, html, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000") + "/api/v1"

# ── Token storage ────────────────────────────────────────────────────────────
TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".auth_token")


def _load_token():
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f).get("access_token")
    except Exception:
        return None


def _save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)


def _clear_token():
    try:
        os.remove(TOKEN_FILE)
    except Exception:
        pass


# ── API helpers ──────────────────────────────────────────────────────────────
def api_headers():
    token = _load_token()
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def api_get(endpoint, params=None):
    try:
        r = requests.get(
            f"{API_BASE}{endpoint}",
            headers=api_headers(),
            params=params,
            timeout=10,
        )
        if r.status_code == 401:
            _clear_token()
            return None, "Session expirée"
        if r.ok:
            return r.json(), None
        return None, r.json().get("detail", "Erreur API")
    except requests.ConnectionError:
        return None, "Service indisponible"
    except requests.Timeout:
        return None, "Délai dépassé"
    except Exception as e:
        return None, str(e)


def api_post(endpoint, data):
    try:
        r = requests.post(
            f"{API_BASE}{endpoint}",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json=data,
            timeout=10,
        )
        if r.ok:
            return r.json(), None
        return None, r.json().get("detail", "Erreur API")
    except requests.ConnectionError:
        return None, "Service indisponible"
    except requests.Timeout:
        return None, "Délai dépassé"
    except Exception as e:
        return None, str(e)


# ── App ──────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="MobiTranz Ministères",
    suppress_callback_exceptions=True,
)

# ── Layouts ──────────────────────────────────────────────────────────────────

login_layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.H3("MobiTranz - Ministères", className="text-center")
                        ),
                        dbc.CardBody(
                            [
                                dbc.Alert(
                                    id="login-alert",
                                    is_open=False,
                                    color="danger",
                                    duration=4000,
                                ),
                                dbc.Label("Téléphone"),
                                dbc.Input(
                                    id="login-phone",
                                    placeholder="+241XXXXXXXX",
                                    type="tel",
                                    className="mb-3",
                                ),
                                dbc.Label("Mot de passe"),
                                dbc.Input(
                                    id="login-password",
                                    placeholder="Mot de passe",
                                    type="password",
                                    className="mb-3",
                                ),
                                dbc.Button(
                                    "Connexion",
                                    id="login-btn",
                                    color="primary",
                                    className="w-100",
                                ),
                                html.Div(
                                    id="login-loading",
                                    className="text-center mt-2",
                                ),
                            ]
                        ),
                    ],
                    className="shadow",
                ),
                width=4,
            ),
            className="vh-100 align-items-center justify-content-center",
        ),
    ],
    fluid=True,
    className="bg-dark",
)

# ── Dashboard page components ────────────────────────────────────────────────

kpi_cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Trajets aujourd'hui"),
                    dbc.CardBody(
                        html.H2(id="kpi-trips", children="—"),
                        className="card-text",
                    ),
                ],
                color="success",
            ),
            width=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Revenus"),
                    dbc.CardBody(
                        html.H2(id="kpi-revenue", children="—"),
                        className="card-text",
                    ),
                ],
                color="primary",
            ),
            width=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Conducteurs actifs"),
                    dbc.CardBody(
                        html.H2(id="kpi-drivers", children="—"),
                        className="card-text",
                    ),
                ],
                color="info",
            ),
            width=3,
        ),
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader("Incidents ouverts"),
                    dbc.CardBody(
                        html.H2(id="kpi-incidents", children="—"),
                        className="card-text",
                    ),
                ],
                color="warning",
            ),
            width=3,
        ),
    ],
    className="mb-4",
)

error_banner = dbc.Alert(
    id="dashboard-alert",
    is_open=False,
    color="danger",
    dismissable=True,
)

charts_row = dbc.Row(
    [
        dbc.Col(dbc.Card([dbc.CardHeader("Trajets par jour"), dbc.CardBody(dcc.Graph(id="chart-trips"))]), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("Revenus par jour"), dbc.CardBody(dcc.Graph(id="chart-revenue"))]), width=6),
    ],
    className="mb-4",
)

charts_row2 = dbc.Row(
    [
        dbc.Col(dbc.Card([dbc.CardHeader("Méthodes de paiement"), dbc.CardBody(dcc.Graph(id="chart-payments"))]), width=6),
        dbc.Col(dbc.Card([dbc.CardHeader("Top conducteurs"), dbc.CardBody(dcc.Graph(id="chart-drivers"))]), width=6),
    ],
    className="mb-4",
)

report_card = dbc.Card(
    [
        dbc.CardHeader("Rapport Ministère des Transports"),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Label("Année"), width=2),
                        dbc.Col(
                            dcc.Dropdown(
                                id="report-year",
                                options=[{"label": str(y), "value": y} for y in range(2024, 2028)],
                                value=date.today().year,
                                className="mb-2",
                                clearable=False,
                            ),
                            width=2,
                        ),
                        dbc.Col(dbc.Label("Mois"), width=1),
                        dbc.Col(
                            dcc.Dropdown(
                                id="report-month",
                                options=[{"label": f"{m:02d}", "value": m} for m in range(1, 13)],
                                value=date.today().month,
                                className="mb-2",
                                clearable=False,
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dbc.Button("Générer", id="report-btn", color="secondary"),
                            width=2,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(id="report-output"),
            ]
        ),
    ],
    className="mb-4",
)

dashboard_layout = dbc.Container(
    [
        dbc.Navbar(
            [
                dbc.NavbarBrand("MobiTranz", href="/"),
                dbc.NavLink("Dashboard", href="/dashboard"),
                dbc.NavLink(
                    "Déconnexion",
                    id="logout-btn",
                    href="/login",
                    className="ms-auto",
                ),
            ],
            color="primary",
            dark=True,
            className="mb-3",
        ),
        error_banner,
        kpi_cards,
        charts_row,
        charts_row2,
        report_card,
        dcc.Interval(id="refresh-timer", interval=60_000, n_intervals=0),
    ],
    fluid=True,
)


# ── Root layout with routing ─────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def route(pathname):
    token = _load_token()
    if pathname == "/login" or not token:
        return login_layout
    return dashboard_layout


# ── Login callback ───────────────────────────────────────────────────────────
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Output("login-alert", "children"),
    Output("login-alert", "is_open"),
    Output("login-loading", "children"),
    Input("login-btn", "n_clicks"),
    State("login-phone", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def do_login(n_clicks, phone, password):
    if not phone or not password:
        return no_update, "Veuillez remplir tous les champs", True, ""

    data, err = api_post("/auth/login", {"phone": phone, "password": password})
    if err:
        return no_update, err, True, ""

    _save_token({
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", ""),
    })
    return "/dashboard", "", False, ""


# ── Logout ───────────────────────────────────────────────────────────────────
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True,
)
def do_logout(n_clicks):
    _clear_token()
    return "/login"


# ── Dashboard data callbacks ─────────────────────────────────────────────────

@app.callback(
    Output("kpi-trips", "children"),
    Output("kpi-revenue", "children"),
    Output("kpi-drivers", "children"),
    Output("kpi-incidents", "children"),
    Output("dashboard-alert", "children"),
    Output("dashboard-alert", "is_open"),
    Input("refresh-timer", "n_intervals"),
    Input("url", "pathname"),
)
def update_kpis(_n, pathname):
    if pathname != "/dashboard":
        return "—", "—", "—", "—", "", False

    data, err = api_get("/analytics/kpis")
    if err:
        return "—", "—", "—", "—", err, True

    rev = f"{data.get('revenue_today', 0):,} XAF"
    return (
        str(data.get("trips_today", "—")),
        rev,
        str(data.get("active_drivers", "—")),
        str(data.get("open_incidents", "—")),
        "",
        False,
    )


@app.callback(
    Output("chart-trips", "figure"),
    Input("refresh-timer", "n_intervals"),
    Input("url", "pathname"),
)
def update_trips_chart(_n, pathname):
    if pathname != "/dashboard":
        return go.Figure()

    data, err = api_get("/analytics/trips/by-day", {"days": 7})
    if err or not data:
        fig = go.Figure()
        fig.add_annotation(text="Service indisponible", showarrow=False)
        return fig

    df = pd.DataFrame(list(data.items()), columns=["date", "count"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    fig = px.bar(df, x="date", y="count", title="Trajets par jour")
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="",
        yaxis_title="Trajets",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig


@app.callback(
    Output("chart-revenue", "figure"),
    Input("refresh-timer", "n_intervals"),
    Input("url", "pathname"),
)
def update_revenue_chart(_n, pathname):
    if pathname != "/dashboard":
        return go.Figure()

    data, err = api_get("/analytics/revenue/by-day", {"days": 7})
    if err or not data:
        fig = go.Figure()
        fig.add_annotation(text="Service indisponible", showarrow=False)
        return fig

    df = pd.DataFrame(list(data.items()), columns=["date", "amount"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    fig = px.line(df, x="date", y="amount", title="Revenus par jour", markers=True)
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="",
        yaxis_title="XAF",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig


@app.callback(
    Output("chart-payments", "figure"),
    Input("refresh-timer", "n_intervals"),
    Input("url", "pathname"),
)
def update_payments_chart(_n, pathname):
    if pathname != "/dashboard":
        return go.Figure()

    data, err = api_get("/analytics/payment-methods")
    if err or not data:
        fig = go.Figure()
        fig.add_annotation(text="Service indisponible", showarrow=False)
        return fig

    df = pd.DataFrame(list(data.items()), columns=["method", "count"])
    fig = px.pie(df, names="method", values="count", title="Méthodes de paiement")
    fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    return fig


@app.callback(
    Output("chart-drivers", "figure"),
    Input("refresh-timer", "n_intervals"),
    Input("url", "pathname"),
)
def update_drivers_chart(_n, pathname):
    if pathname != "/dashboard":
        return go.Figure()

    data, err = api_get("/analytics/drivers/top", {"limit": 10})
    if err or not data:
        fig = go.Figure()
        fig.add_annotation(text="Service indisponible", showarrow=False)
        return fig

    df = pd.DataFrame(data)
    if df.empty:
        return go.Figure()

    df["label"] = df["id"].str[:8] + "…"
    fig = px.bar(
        df,
        x="label",
        y="total_earnings",
        title="Top conducteurs (revenus)",
        hover_data=["total_trips", "rating"],
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Conducteur",
        yaxis_title="Revenus (XAF)",
        margin=dict(l=20, r=20, t=30, b=20),
    )
    return fig


# ── Ministry report ──────────────────────────────────────────────────────────
@app.callback(
    Output("report-output", "children"),
    Input("report-btn", "n_clicks"),
    State("report-year", "value"),
    State("report-month", "value"),
    prevent_initial_call=True,
)
def generate_report(n_clicks, year, month):
    data, err = api_get("/analytics/ministry-report", {"year": year, "month": month})
    if err:
        return dbc.Alert(err, color="danger")

    return dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Indicateur"), html.Th("Valeur")])),
            html.Tbody(
                [
                    html.Tr([html.Td("Période"), html.Td(data.get("period", "—"))]),
                    html.Tr([html.Td("Trajets"), html.Td(f"{data.get('total_trips', 0):,}")]),
                    html.Tr([html.Td("Revenus"), html.Td(f"{data.get('total_revenue_xaf', 0):,} XAF")]),
                    html.Tr([html.Td("Incidents"), html.Td(str(data.get('total_incidents', 0)))]),
                    html.Tr([html.Td("Généré le"), html.Td(data.get("generated_at", "—"))]),
                ]
            ),
        ],
        striped=True,
        bordered=True,
        hover=True,
        dark=True,
    )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
