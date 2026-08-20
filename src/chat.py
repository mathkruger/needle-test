import needle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

EXIT_TEXT = "exit"

BANNER = r"""
 ___ ___ ___     _   ___ 
| _ \ __/ __|   /_\ |_ _|
|   / _| (_ |  / _ \ | | 
|_|_\___\___| /_/ \_\___|

"""

console = Console()


def format_tool_results(results: list) -> None:
    if not results:
        return

    for item in results:
        if not isinstance(item, dict):
            console.print(Panel(str(item), border_style="dim", title="Result"))
            continue

        if "error" in item:
            console.print(
                Panel(
                    f"[bold red]Error:[/bold red] {item['error']}",
                    border_style="red",
                    title="Tool Error",
                )
            )
            continue

        labels = item.pop("__labels__", {}) if "__labels__" in item else {}

        table = Table(
            show_header=False,
            border_style="dim",
            padding=(0, 2),
            title="Result",
        )
        table.add_column("Key", style="bold cyan", no_wrap=True)
        table.add_column("Value")

        for key, value in item.items():
            label = labels.get(key, key.replace("_", " ").title())
            formatted = format_value(key, value)
            table.add_row(label, formatted)

        console.print(table)


def _render_nested_dict(data: dict) -> Table:
    t = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    t.add_column("Field", style="cyan", no_wrap=True)
    t.add_column("Value")
    for k, v in data.items():
        t.add_row(k, format_value(k, v))
    return t


def _render_list_of_dicts(items: list[dict]) -> Table:
    if not items:
        return _render_nested_dict({})

    keys = list(items[0].keys())
    t = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    for k in keys:
        t.add_column(k, style="cyan")
    for item in items:
        t.add_row(*(format_value(k, item.get(k, "")) for k in keys))
    return t


def format_value(key: str, value) -> str | Table:
    if isinstance(value, dict):
        return _render_nested_dict(value)
    if isinstance(value, list) and value and isinstance(value[0], dict):
        return _render_list_of_dicts(value)
    if isinstance(value, float):
        if "percent" in key:
            return f"{value:.1f}%"
        if "mb" in key or "gb" in key:
            return f"{value:,.1f} MB"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def format_metrics(result: dict) -> None:
    parts = []
    prefill_tps = result.get("prefill_tps")
    decode_tps = result.get("decode_tps")
    peak_ram = result.get("peak_ram_mb")
    confidence = result.get("confidence")

    if prefill_tps is not None:
        parts.append(f"prefill {prefill_tps:,.1f} tok/s")
    if decode_tps is not None:
        parts.append(f"decode {decode_tps:,.1f} tok/s")
    if peak_ram is not None:
        parts.append(f"peak ram {peak_ram:,.1f} MB")
    if confidence is not None:
        parts.append(f"confidence {confidence:.4f}")

    if parts:
        console.print(f"[dim]  {' · '.join(parts)}[/dim]")


def init_chat(agent: needle.Needle):
    console.print()
    console.print(
        Panel(
            BANNER,
            border_style="bold cyan",
            subtitle="[dim]type '[bold]'exit'[/bold]' to quit[/dim]",
            subtitle_align="center",
        )
    )
    console.print()

    prompt = ""
    while prompt != EXIT_TEXT:
        prompt = console.input("[bold cyan]>[/bold cyan] ")
        if prompt.strip() == "":
            continue
        if prompt != EXIT_TEXT:
            result = agent.run(prompt)

            reasoning = result.get("reasoning", "").strip()
            if reasoning:
                console.print()
                console.print(
                    Panel(
                        reasoning,
                        border_style="dim",
                        title="[dim]Reasoning[/dim]",
                        title_align="left",
                    )
                )

            results = result.get("results", [])
            if results:
                console.print()
                format_tool_results(results)

            format_metrics(result)
            console.print()
        else:
            console.print()
            console.print(
                Panel(
                    "[bold]Goodbye![/bold] See you next time.",
                    border_style="bold cyan",
                )
            )
            console.print()
