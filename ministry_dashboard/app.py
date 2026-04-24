# ============================================================
# Point d'entrée Dashboard Ministères
# Fichier : ministry_dashboard/app.py
# Description : Application Dash pour ministères
# ============================================================

from dash import Dash
import dash_bootstrap_components as dbc


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="MobiTranz Ministères"
)


app.layout = dbc.Container([
    dbc.Navbar(
        [
            dbc.NavbarBrand("MobiTranz", href="/"),
            dbc.NavLink("Trafic", href="/traffic"),
            dbc.NavLink("Finances", href="/finance"),
            dbc.NavLink("Conducteurs", href="/drivers"),
            dbc.NavLink("Incidents", href="/incidents"),
            dbc.NavLink("Rapports", href="/reports"),
        ],
        color="primary",
        dark=True,
    ),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Trajets aujourd'hui"),
                    dbc.CardBody("145", className="card-text"),
                ], color="success")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Revenus"),
                    dbc.CardBody("1,234,000 XAF", className="card-text"),
                ], color="primary")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Conducteurs actifs"),
                    dbc.CardBody("42", className="card-text"),
                ], color="info")
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Incidents"),
                    dbc.CardBody("2", className="card-text"),
                ], color="warning")
            ], width=3),
        ], className="mb-4 mt-4"),
    ]),
], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True)