"""Command-line interface for AI File Concierge."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from src.agents.file_concierge import FileConcierge


class CLI:
    """Command-line interface handler."""

    def __init__(self):
        self.console = Console()
        self.concierge = FileConcierge()

    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# AI File Concierge

Welcome to your intelligent file assistant!

## Available Commands:
- Ask natural language questions about your files
- Type **index** to index all files in the sandbox
- Type **stats** to see system statistics
- Type **help** for more information
- Type **exit** or **quit** to exit

## Example Queries:
- "Find my Python files"
- "Search for documents about machine learning"
- "Create a collection for all job application files"
- "Suggest tags for notes/meeting.txt"
"""
        self.console.print(Panel(Markdown(welcome_text), title="AI File Concierge", border_style="cyan"))

    def run(self):
        """Run the interactive REPL."""
        self.display_welcome()

        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

                if not user_input.strip():
                    continue

                # Handle special commands
                command = user_input.strip().lower()

                if command in ["exit", "quit", "q"]:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                elif command == "index":
                    self.concierge.index_all_files()

                elif command == "stats":
                    self.concierge.display_stats()

                elif command == "help":
                    self.display_welcome()

                elif command == "reindex":
                    self.concierge.index_all_files(force_reindex=True)

                else:
                    # Process as agent query
                    self.console.print("[bold green]Agent:[/bold green]", end=" ")
                    response = self.concierge.query(user_input)
                    self.console.print(response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                continue

            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")


@click.group()
def cli():
    """AI File Concierge - Intelligent file organization assistant."""
    pass


@cli.command()
def interactive():
    """Start interactive REPL mode."""
    cli_interface = CLI()
    cli_interface.run()


@cli.command()
def index():
    """Index all files in the sandbox directory."""
    concierge = FileConcierge()
    concierge.index_all_files()


@cli.command()
@click.argument("query")
def search(query):
    """Search files using a natural language query."""
    concierge = FileConcierge()
    console = Console()

    console.print(f"[bold cyan]Searching for:[/bold cyan] {query}")
    response = concierge.query(query)
    console.print(f"\n[bold green]Results:[/bold green]\n{response}")


@cli.command()
def stats():
    """Display system statistics."""
    concierge = FileConcierge()
    concierge.display_stats()


if __name__ == "__main__":
    cli()
