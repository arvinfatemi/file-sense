"""Command-line interface for AI File Concierge."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from src.file_concierge.indexer import FileIndexer
from agents.file_concierge.agent import query_agent


class CLI:
    """Command-line interface handler."""

    def __init__(self):
        self.console = Console()
        self.indexer = FileIndexer()

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
                    self.indexer.index_all_files()

                elif command == "stats":
                    self.indexer.display_stats()

                elif command == "help":
                    self.display_welcome()

                elif command == "reindex":
                    self.indexer.index_all_files(force_reindex=True)

                else:
                    # Process as agent query using ADK
                    self.console.print("[bold green]Agent:[/bold green] ", end="")
                    try:
                        # Use ADK agent to process the query
                        response = query_agent(user_input)
                        self.console.print(response)
                    except Exception as e:
                        self.console.print(f"[red]Error processing query: {str(e)}[/red]")

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
    indexer = FileIndexer()
    indexer.index_all_files()


@cli.command()
@click.argument("query")
def search(query):
    """Search files using a natural language query."""
    console = Console()

    console.print(f"[bold cyan]Searching for:[/bold cyan] {query}")
    try:
        response = query_agent(query)
        console.print(f"\n[bold green]Results:[/bold green]\n{response}")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
def stats():
    """Display system statistics."""
    indexer = FileIndexer()
    indexer.display_stats()


if __name__ == "__main__":
    cli()
