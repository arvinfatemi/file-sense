"""
Evaluation scenarios for AI File Concierge.

Tests search accuracy, tagging quality, and workflow completion.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.file_concierge import FileConcierge
from src.tools.search_tools import SearchTools
from src.tools.tag_tools import TagTools
from src.indexing.vector_store import VectorStore
from src.memory.long_term import LongTermMemory
from rich.console import Console
from rich.table import Table


class Evaluator:
    """Evaluates the File Concierge system."""

    def __init__(self):
        self.console = Console()
        self.concierge = FileConcierge()
        self.search_tools = SearchTools()
        self.tag_tools = TagTools()

        # Ensure files are indexed
        self.console.print("[cyan]Indexing files for evaluation...[/cyan]")
        self.concierge.index_all_files()

    def evaluate_search_accuracy(self):
        """Evaluate semantic search accuracy using test queries."""
        self.console.print("\n[bold cyan]Testing Search Accuracy[/bold cyan]\n")

        test_cases = [
            {
                "query": "machine learning and Bayesian methods",
                "expected_files": ["code/ml_experiment.py"],
                "description": "ML-related code search"
            },
            {
                "query": "job application materials",
                "expected_files": ["documents/resume.txt", "documents/cover_letter.txt"],
                "description": "Job search documents"
            },
            {
                "query": "meeting notes and action items",
                "expected_files": ["notes/meeting_notes.txt"],
                "description": "Meeting documentation"
            },
            {
                "query": "transformer architecture and attention mechanisms",
                "expected_files": ["documents/research_paper_notes.md"],
                "description": "Research notes search"
            },
            {
                "query": "data processing and pandas",
                "expected_files": ["code/data_processing.py"],
                "description": "Data engineering code"
            }
        ]

        results = []
        for test_case in test_cases:
            search_result = self.search_tools.semantic_search(test_case["query"], top_k=5)

            if search_result.get("success"):
                retrieved_files = [r["file_path"] for r in search_result["results"]]

                # Calculate Hit@K
                hits = sum(1 for expected in test_case["expected_files"] if expected in retrieved_files)
                hit_rate = hits / len(test_case["expected_files"])

                results.append({
                    "query": test_case["query"],
                    "description": test_case["description"],
                    "hit_rate": hit_rate,
                    "retrieved": len(retrieved_files),
                    "expected": len(test_case["expected_files"]),
                    "success": hit_rate > 0
                })

        # Display results
        table = Table(title="Search Accuracy Results")
        table.add_column("Test Case", style="cyan")
        table.add_column("Hit Rate", style="green")
        table.add_column("Status", style="bold")

        for result in results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            status_style = "green" if result["success"] else "red"
            table.add_row(
                result["description"],
                f"{result['hit_rate']:.1%}",
                f"[{status_style}]{status}[/{status_style}]"
            )

        self.console.print(table)

        # Calculate overall accuracy
        avg_hit_rate = sum(r["hit_rate"] for r in results) / len(results)
        pass_rate = sum(1 for r in results if r["success"]) / len(results)

        self.console.print(f"\n[bold]Overall Hit Rate:[/bold] {avg_hit_rate:.1%}")
        self.console.print(f"[bold]Pass Rate:[/bold] {pass_rate:.1%}")

        return results

    def evaluate_tagging_quality(self):
        """Evaluate tag suggestion quality."""
        self.console.print("\n[bold cyan]Testing Tag Suggestion Quality[/bold cyan]\n")

        test_files = [
            {
                "file": "documents/resume.txt",
                "expected_themes": ["career", "resume", "job", "engineering", "professional"]
            },
            {
                "file": "code/ml_experiment.py",
                "expected_themes": ["machine-learning", "python", "bayesian", "statistics", "code"]
            },
            {
                "file": "notes/meeting_notes.txt",
                "expected_themes": ["meeting", "work", "team", "planning", "notes"]
            }
        ]

        results = []
        for test_file in test_files:
            # Read file
            file_result = self.concierge.orchestrator.file_tools.read_file(test_file["file"])

            if file_result.get("success"):
                # Get tag suggestions
                tag_result = self.tag_tools.suggest_tags(
                    test_file["file"],
                    file_result.get("content", "")
                )

                if tag_result.get("success"):
                    suggested_tags = tag_result.get("suggested_tags", [])

                    # Check if any expected themes are present
                    matches = sum(
                        1 for expected in test_file["expected_themes"]
                        if any(expected in tag.lower() for tag in suggested_tags)
                    )

                    relevance = matches / len(test_file["expected_themes"]) if test_file["expected_themes"] else 0

                    results.append({
                        "file": test_file["file"],
                        "suggested_tags": suggested_tags,
                        "relevance": relevance,
                        "success": relevance > 0.3
                    })

        # Display results
        table = Table(title="Tag Suggestion Quality")
        table.add_column("File", style="cyan")
        table.add_column("Suggested Tags", style="yellow")
        table.add_column("Relevance", style="green")
        table.add_column("Status", style="bold")

        for result in results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            status_style = "green" if result["success"] else "red"
            table.add_row(
                result["file"],
                ", ".join(result["suggested_tags"][:5]),
                f"{result['relevance']:.1%}",
                f"[{status_style}]{status}[/{status_style}]"
            )

        self.console.print(table)

        return results

    def evaluate_workflow_scenario(self):
        """Evaluate end-to-end workflow: search, tag, and create collection."""
        self.console.print("\n[bold cyan]Testing End-to-End Workflow[/bold cyan]\n")

        steps = []

        try:
            # Step 1: Search for job-related files
            self.console.print("Step 1: Searching for job application files...")
            search_result = self.search_tools.semantic_search("job application", top_k=5)
            steps.append({"step": "Search", "success": search_result.get("success", False)})

            if search_result.get("success"):
                job_files = [r["file_path"] for r in search_result["results"][:2]]
                self.console.print(f"  Found {len(job_files)} files")

                # Step 2: Apply tags
                self.console.print("\nStep 2: Applying tags...")
                for file_path in job_files:
                    tag_result = self.tag_tools.apply_tags(file_path, ["job-search", "career"])
                    steps.append({"step": f"Tag {file_path}", "success": tag_result.get("success", False)})
                    self.console.print(f"  Tagged {file_path}")

                # Step 3: Create collection
                self.console.print("\nStep 3: Creating collection...")
                collection_result = self.concierge.orchestrator.collection_tools.create_collection(
                    "Job Applications",
                    "All files related to job search"
                )
                steps.append({"step": "Create Collection", "success": collection_result.get("success", False)})

                if collection_result.get("success"):
                    # Add files to collection
                    for file_path in job_files:
                        add_result = self.concierge.orchestrator.collection_tools.add_to_collection(
                            "Job Applications",
                            file_path
                        )
                        steps.append({"step": f"Add to Collection", "success": add_result.get("success", False)})

                    self.console.print(f"  Created collection with {len(job_files)} files")

        except Exception as e:
            self.console.print(f"[red]Error during workflow: {str(e)}[/red]")
            steps.append({"step": "Workflow", "success": False})

        # Display results
        table = Table(title="Workflow Scenario Results")
        table.add_column("Step", style="cyan")
        table.add_column("Status", style="bold")

        for step in steps:
            status = "✓ SUCCESS" if step["success"] else "✗ FAILED"
            status_style = "green" if step["success"] else "red"
            table.add_row(step["step"], f"[{status_style}]{status}[/{status_style}]")

        self.console.print("\n", table)

        success_rate = sum(1 for s in steps if s["success"]) / len(steps) if steps else 0
        self.console.print(f"\n[bold]Workflow Success Rate:[/bold] {success_rate:.1%}")

        return steps

    def run_all_evaluations(self):
        """Run all evaluation scenarios."""
        self.console.print("[bold green]Starting AI File Concierge Evaluation[/bold green]")

        search_results = self.evaluate_search_accuracy()
        tag_results = self.evaluate_tagging_quality()
        workflow_results = self.evaluate_workflow_scenario()

        self.console.print("\n[bold green]Evaluation Complete![/bold green]")

        return {
            "search": search_results,
            "tagging": tag_results,
            "workflow": workflow_results
        }


if __name__ == "__main__":
    evaluator = Evaluator()
    results = evaluator.run_all_evaluations()
