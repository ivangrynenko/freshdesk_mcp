import asyncio
import json
from typing import Optional

import typer

from . import server

app = typer.Typer(add_completion=False, help="Freshdesk CLI (wraps freshdesk-mcp functions)")

tickets_app = typer.Typer(help="Ticket operations")
companies_app = typer.Typer(help="Company operations")

app.add_typer(tickets_app, name="tickets")
app.add_typer(companies_app, name="companies")


def _print(data, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(data, indent=2, sort_keys=True, default=str))
    else:
        typer.echo(str(data))


def _run(coro):
    return asyncio.run(coro)


@app.command("validate-env")
def validate_env() -> None:
    """Validate required environment variables are present."""

    missing = []
    if not server.freshdesk_domain():
        missing.append("FRESHDESK_DOMAIN")
    if not server.freshdesk_api_key():
        missing.append("FRESHDESK_API_KEY")

    if missing:
        typer.echo(
            f"Error: Missing required environment variables: {', '.join(missing)}",
            err=True,
        )
        raise typer.Exit(code=2)


@tickets_app.command("get")
def ticket_get(ticket_id: int, json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """Get a ticket."""

    data = _run(server.get_ticket(ticket_id))
    _print(data, json_out)


@tickets_app.command("search")
def ticket_search(query: str, json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """Search tickets using Freshdesk search syntax."""

    data = _run(server.search_tickets(query))
    _print(data, json_out)


@tickets_app.command("delete")
def ticket_delete(ticket_id: int, json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """Delete a ticket."""

    data = _run(server.delete_ticket(ticket_id))
    _print(data, json_out)


@tickets_app.command("reply")
def ticket_reply(
    ticket_id: int,
    body: str = typer.Option(..., "--body", help="Reply body"),
    json_out: bool = typer.Option(True, "--json/--text"),
) -> None:
    """Create a reply on a ticket."""

    data = _run(server.create_ticket_reply(ticket_id, body))
    _print(data, json_out)


@companies_app.command("list")
def company_list(json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """List companies."""

    data = _run(server.list_companies())
    _print(data, json_out)


@companies_app.command("get")
def company_get(company_id: int, json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """View a company by id."""

    data = _run(server.view_company(company_id))
    _print(data, json_out)


@companies_app.command("search")
def company_search(
    name: str,
    json_out: bool = typer.Option(True, "--json/--text"),
) -> None:
    """Search companies by name."""

    data = _run(server.search_companies(name))
    _print(data, json_out)


@companies_app.command("fields")
def company_fields(json_out: bool = typer.Option(True, "--json/--text")) -> None:
    """List company fields."""

    data = _run(server.list_company_fields())
    _print(data, json_out)


def main() -> None:
    app()
