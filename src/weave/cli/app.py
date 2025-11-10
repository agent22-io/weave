"""Main Typer CLI application for Weave."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .. import __version__
from ..core.exceptions import ConfigError, GraphError, WeaveError
from ..core.graph import DependencyGraph
from ..parser.config import load_config_from_path
from ..plugins.manager import PluginManager
from ..plugins.base import PluginCategory
from ..runtime.executor import MockExecutor
from .output import WeaveOutput

app = typer.Typer(
    name="weave",
    help="🧵 Weave - Declarative agent orchestration framework",
    add_completion=False,
)

console = Console()
output = WeaveOutput(console)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"Weave version {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Weave CLI - Declarative agent orchestration."""
    pass


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
    template: str = typer.Option("basic", "--template", "-t", help="Template to use"),
) -> None:
    """
    Initialize a new Weave project with example configuration.

    Creates a .weave.yaml file with sample agents and weaves.
    """
    config_path = Path(".weave.yaml")

    if config_path.exists() and not force:
        output.print_error(
            Exception(
                f"{config_path} already exists. Use --force to overwrite."
            )
        )
        raise typer.Exit(1)

    # Example configuration
    example_config = """# Weave Configuration
# https://docs.weave.dev

version: "1.0"

# Optional: define environment variables
# env:
#   DEFAULT_MODEL: "gpt-4"

agents:
  researcher:
    model: "gpt-4"
    tools:
      - web_search
      - summarizer
    config:
      temperature: 0.7
      max_tokens: 1000
    outputs: "research_summary"

  writer:
    model: "claude-3-opus"
    tools:
      - text_generator
    inputs: "researcher"  # Takes input from researcher
    config:
      temperature: 0.9
      max_tokens: 2000
    outputs: "draft_article"

  editor:
    model: "gpt-4"
    tools:
      - grammar_checker
      - fact_checker
    inputs: "writer"
    config:
      temperature: 0.3
    outputs: "final_article"

weaves:
  content_pipeline:
    description: "Research, write, and edit content"
    agents:
      - researcher
      - writer
      - editor
"""

    try:
        with open(config_path, "w") as f:
            f.write(example_config)

        console.print("\n✨ [bold green]Initialized Weave project![/bold green]\n")
        console.print(f"Created [cyan]{config_path}[/cyan] with example configuration\n")
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Edit .weave.yaml to define your agents")
        console.print("  2. Run [cyan]weave plan[/cyan] to preview execution")
        console.print("  3. Run [cyan]weave apply[/cyan] to execute the flow\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def plan(
    config: Path = typer.Option(
        ".weave.yaml", "--config", "-c", help="Path to config file"
    ),
    weave: Optional[str] = typer.Option(
        None, "--weave", "-w", help="Specific weave to plan"
    ),
) -> None:
    """
    Preview execution plan without running agents.

    Parses configuration, validates structure, and shows the execution graph.
    """
    try:
        # Load config
        console.print(f"\n📋 Loading configuration from [cyan]{config}[/cyan]...")
        weave_config = load_config_from_path(config)
        console.print("[green]✅ Configuration valid[/green]\n")

        # Determine which weave to plan
        if weave:
            if weave not in weave_config.weaves:
                available = ", ".join(weave_config.weaves.keys())
                raise WeaveError(f"Weave '{weave}' not found. Available: {available}")
            weave_name = weave
        else:
            # Use first weave
            weave_name = list(weave_config.weaves.keys())[0]
            if len(weave_config.weaves) > 1:
                console.print(
                    f"[dim]Using weave: {weave_name} "
                    f"(specify with --weave to use another)[/dim]\n"
                )

        # Build graph
        graph = DependencyGraph(weave_config)
        graph.build(weave_name)
        graph.validate()

        # Display plan
        output.print_plan(weave_config, weave_name, graph)

        console.print(
            f"[dim]Run [cyan]weave apply[/cyan] to execute this plan.[/dim]\n"
        )

    except (ConfigError, GraphError, WeaveError) as e:
        output.print_error(e)
        raise typer.Exit(1)
    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def apply(
    config: Path = typer.Option(
        ".weave.yaml", "--config", "-c", help="Path to config file"
    ),
    weave: Optional[str] = typer.Option(
        None, "--weave", "-w", help="Specific weave to apply"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be executed without running"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Verbose output"
    ),
) -> None:
    """
    Execute the agent flow.

    Runs all agents in the weave according to their dependency order.
    In v1, this uses mock execution. Future versions will support real LLM calls.
    """
    try:
        # Load config
        console.print(f"\n📋 Loading configuration from [cyan]{config}[/cyan]...")
        weave_config = load_config_from_path(config)

        # Determine which weave to apply
        if weave:
            if weave not in weave_config.weaves:
                available = ", ".join(weave_config.weaves.keys())
                raise WeaveError(f"Weave '{weave}' not found. Available: {available}")
            weave_name = weave
        else:
            weave_name = list(weave_config.weaves.keys())[0]
            if len(weave_config.weaves) > 1:
                console.print(
                    f"[dim]Using weave: {weave_name} "
                    f"(specify with --weave to use another)[/dim]\n"
                )

        # Build graph
        graph = DependencyGraph(weave_config)
        graph.build(weave_name)
        graph.validate()

        # Execute
        executor = MockExecutor(console=console, verbose=verbose)
        summary = executor.execute_flow(graph, weave_name, dry_run=dry_run)

        # Exit with error if any failed
        if summary.failed > 0:
            raise typer.Exit(1)

    except (ConfigError, GraphError, WeaveError) as e:
        output.print_error(e)
        raise typer.Exit(1)
    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def graph(
    config: Path = typer.Option(
        ".weave.yaml", "--config", "-c", help="Path to config file"
    ),
    weave: Optional[str] = typer.Option(
        None, "--weave", "-w", help="Specific weave to visualize"
    ),
    format: str = typer.Option(
        "ascii", "--format", "-f", help="Output format (ascii, mermaid)"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save to file instead of stdout"
    ),
) -> None:
    """
    Visualize the dependency graph.

    Shows how agents are connected and their execution order.
    Supports ASCII art and Mermaid diagram formats.
    """
    try:
        # Load config
        weave_config = load_config_from_path(config)

        # Determine which weave to visualize
        if weave:
            if weave not in weave_config.weaves:
                available = ", ".join(weave_config.weaves.keys())
                raise WeaveError(f"Weave '{weave}' not found. Available: {available}")
            weave_name = weave
        else:
            weave_name = list(weave_config.weaves.keys())[0]

        # Build graph
        dep_graph = DependencyGraph(weave_config)
        dep_graph.build(weave_name)
        dep_graph.validate()

        # Generate visualization
        if format == "ascii":
            result = dep_graph.to_ascii()
        elif format == "mermaid":
            result = dep_graph.to_mermaid()
        else:
            raise WeaveError(f"Unknown format: {format}. Use 'ascii' or 'mermaid'")

        # Output
        if output_file:
            with open(output_file, "w") as f:
                f.write(result)
            console.print(f"\n[green]✅ Graph saved to {output_file}[/green]\n")
        else:
            console.print(f"\n📊 Dependency Graph: [bold cyan]{weave_name}[/bold cyan]\n")
            console.print(result)
            console.print()

            # Show execution order
            order = dep_graph.get_execution_order()
            console.print(f"[bold]Execution order:[/bold] {' → '.join(order)}\n")

    except (ConfigError, GraphError, WeaveError) as e:
        output.print_error(e)
        raise typer.Exit(1)
    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def plugins(
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
) -> None:
    """
    List available plugins.

    Shows all built-in and loaded plugins with their metadata.
    """
    try:
        # Create plugin manager
        manager = PluginManager(console=console)
        manager.load_builtin_plugins()

        # Filter by category if specified
        plugin_category = None
        if category:
            try:
                plugin_category = PluginCategory(category)
            except ValueError:
                valid_categories = ", ".join(c.value for c in PluginCategory)
                console.print(
                    f"[red]Invalid category: {category}[/red]\n"
                    f"Valid categories: {valid_categories}"
                )
                raise typer.Exit(1)

        # List plugins
        manager.list_plugins(category=plugin_category, verbose=verbose)

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
