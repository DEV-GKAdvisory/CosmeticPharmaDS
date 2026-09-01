"""Dash multi-page app for cosmetic pharma model comparison."""

from __future__ import annotations

from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

APP_TITLE = "Cosmetic Pharma DS"
PAGES_DIR = Path(__file__).resolve().parent / "pages"


def create_app() -> Dash:
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder=str(PAGES_DIR),
        external_stylesheets=[dbc.themes.FLATLY],
        suppress_callback_exceptions=True,
        title=APP_TITLE,
    )

    navbar = dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(APP_TITLE, href="/"),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Compare models", href="/")),
                        dbc.NavItem(
                            dbc.NavLink("Model descriptions", href="/models")
                        ),
                    ],
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        className="mb-4",
    )

    app.layout = dbc.Container(
        [navbar, dash.page_container],
        fluid=True,
        className="pb-5",
    )
    return app


def main() -> None:
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
