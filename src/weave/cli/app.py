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
from ..resources.loader import ResourceLoader
from ..resources.models import ResourceType
from ..runtime.executor import Executor
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

    Creates a .agent.yaml file and .agent/ directory with resource subdirectories.
    """
    config_path = Path(".agent.yaml")
    agent_dir = Path(".agent")

    if config_path.exists() and not force:
        output.print_error(
            Exception(
                f"{config_path} already exists. Use --force to overwrite."
            )
        )
        raise typer.Exit(1)

    # Example configuration
    example_config = """# Agent Configuration
# https://docs.weave.dev

version: "1.0"

# Optional: define environment variables
# env:
#   DEFAULT_MODEL: "gpt-4"

agents:
  researcher:
    model: "gpt-4"
    tools:
      - http_request
      - file_read
      - json_validator
    config:
      temperature: 0.7
      max_tokens: 1000
    outputs: "research_summary"

  writer:
    model: "claude-3-opus"
    tools:
      - text_length
      - string_formatter
    inputs: "researcher"  # Takes input from researcher
    config:
      temperature: 0.9
      max_tokens: 2000
    outputs: "draft_article"

  editor:
    model: "gpt-4"
    tools:
      - file_write
      - text_length
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

    # Resource subdirectories to create
    resource_dirs = [
        "prompts",
        "skills",
        "recipes",
        "knowledge",
        "rules",
        "behaviors",
        "sub_agents"
    ]

    try:
        # Create config file
        with open(config_path, "w") as f:
            f.write(example_config)

        # Create .agent directory with resource subdirectories
        agent_dir.mkdir(exist_ok=True)
        for subdir in resource_dirs:
            (agent_dir / subdir).mkdir(exist_ok=True)
            # Create .gitkeep to preserve empty directories in git
            (agent_dir / subdir / ".gitkeep").touch()

        console.print("\n✨ [bold green]Initialized Weave project![/bold green]\n")
        console.print(f"Created [cyan]{config_path}[/cyan] with example configuration")
        console.print(f"Created [cyan]{agent_dir}/[/cyan] directory with resource folders:\n")
        for subdir in resource_dirs:
            console.print(f"  • {agent_dir}/{subdir}/")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Edit .agent.yaml to define your agents")
        console.print("  2. Add resources to .agent/ subdirectories")
        console.print("  3. Run [cyan]weave plan[/cyan] to preview execution")
        console.print("  4. Run [cyan]weave apply[/cyan] to execute the flow\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def plan(
    config: Path = typer.Option(
        ".agent.yaml", "--config", "-c", help="Path to config file"
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
        ".agent.yaml", "--config", "-c", help="Path to config file"
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
    Execute the agent flow with real LLM API calls.

    Requires API keys configured via environment variables.
    """
    try:
        import asyncio

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

        # Execute with real LLMs
        console.print("[bold green]🚀 Executing workflow[/bold green]")
        if not dry_run:
            console.print("[dim]Using actual LLM APIs (costs may apply)[/dim]\n")

        executor = Executor(
            console=console,
            verbose=verbose,
            config=weave_config
        )
        summary = asyncio.run(executor.execute_flow(graph, weave_name, dry_run=dry_run))

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


@app.command()
def resources(
    type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Filter by resource type"
    ),
    path: Path = typer.Option(
        ".agent", "--path", "-p", help="Resources directory path"
    ),
    create: bool = typer.Option(
        False, "--create", help="Create default resource structure"
    ),
) -> None:
    """
    List and manage resources (prompts, skills, recipes, etc.).

    Resources are loaded from the .agent/ directory by default.
    """
    try:
        loader = ResourceLoader(base_path=path)

        # Create structure if requested
        if create:
            loader.create_default_structure()
            console.print(f"\n✨ [bold green]Created resource structure in {path}[/bold green]\n")
            console.print("Created directories:")
            console.print("  • prompts/     - System prompts")
            console.print("  • skills/      - Agent skills")
            console.print("  • recipes/     - Workflow recipes")
            console.print("  • knowledge/   - Knowledge bases")
            console.print("  • rules/       - Behavioral rules")
            console.print("  • behaviors/   - Agent behaviors")
            console.print("  • sub_agents/  - Sub-agent configurations\n")
            console.print("[dim]Example files have been created in each directory.[/dim]\n")
            return

        # Load resources
        loader.load_all()

        # Filter by type if specified
        resource_type = None
        if type:
            try:
                resource_type = ResourceType(type)
            except ValueError:
                valid_types = ", ".join(rt.value for rt in ResourceType)
                console.print(
                    f"[red]Invalid type: {type}[/red]\n"
                    f"Valid types: {valid_types}"
                )
                raise typer.Exit(1)

        # Get resources
        resources_dict = loader.list_resources(resource_type)

        # Display
        from rich.table import Table

        table = Table(title="Available Resources", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Names", style="white")

        for res_type, names in resources_dict.items():
            if names:  # Only show types with resources
                names_str = ", ".join(names) if len(names) <= 5 else f"{', '.join(names[:5])}, ..."
                table.add_row(res_type, str(len(names)), names_str)

        console.print("\n")
        console.print(table)

        # Summary
        total = sum(len(names) for names in resources_dict.values())
        console.print(f"\n[bold]Total resources:[/bold] {total}")
        console.print(f"[dim]Location: {path}[/dim]\n")

        if total == 0:
            console.print("[yellow]No resources found. Use --create to initialize.[/yellow]\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def tools(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Filter by tags (comma-separated)"),
    schema: Optional[str] = typer.Option(None, "--schema", "-s", help="Show JSON schema for a specific tool"),
) -> None:
    """
    List and inspect available tools for agents.

    Shows built-in tools and tools from configured MCP servers.
    """
    try:
        from ..tools.executor import ToolExecutor
        from rich.table import Table
        from rich.json import JSON
        import json as json_module

        executor = ToolExecutor()

        # Show schema for specific tool
        if schema:
            tool = executor.get_tool(schema)
            if not tool:
                console.print(f"[red]Tool not found: {schema}[/red]")
                raise typer.Exit(1)

            console.print(f"\n[bold cyan]Tool Schema: {schema}[/bold cyan]\n")
            schema_json = tool.definition.to_json_schema()
            console.print(JSON(json_module.dumps(schema_json, indent=2)))
            console.print()
            return

        # Parse tags filter
        tags_list = None
        if tags:
            tags_list = [t.strip() for t in tags.split(",")]

        # Get tools
        tool_defs = executor.list_tools(category=category, tags=tags_list)

        if not tool_defs:
            console.print("[yellow]No tools found matching the criteria.[/yellow]")
            raise typer.Exit(0)

        # Create table
        table = Table(title="Available Tools", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="green")
        table.add_column("Description", style="white")
        table.add_column("Source", style="yellow")

        for tool_def in sorted(tool_defs, key=lambda t: t.name):
            source = tool_def.mcp_server if tool_def.mcp_server else "built-in"
            desc = tool_def.description[:60] + "..." if len(tool_def.description) > 60 else tool_def.description
            table.add_row(tool_def.name, tool_def.category, desc, source)

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold]Total tools:[/bold] {len(tool_defs)}")
        console.print("[dim]Use --schema <tool_name> to see detailed schema[/dim]\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def mcp(
    list_servers: bool = typer.Option(False, "--list", "-l", help="List configured MCP servers"),
    add: Optional[str] = typer.Option(None, "--add", help="Add a new MCP server (name)"),
    command: Optional[str] = typer.Option(None, "--command", help="Command to start server (used with --add)"),
    remove: Optional[str] = typer.Option(None, "--remove", help="Remove an MCP server"),
    init: bool = typer.Option(False, "--init", help="Create example MCP configuration"),
    server_tools: Optional[str] = typer.Option(None, "--server-tools", help="List tools from specific server"),
) -> None:
    """
    Manage MCP (Model Context Protocol) servers.

    Configure and manage external tool providers via MCP.
    """
    try:
        from ..tools.mcp_client import MCPClient, MCPServer
        from rich.table import Table

        client = MCPClient()

        # Initialize example config
        if init:
            client.create_example_config()
            console.print(f"\n✨ [bold green]Created MCP configuration[/bold green]\n")
            console.print(f"Location: {client.config_path}")
            console.print("\nExample servers configured:")
            console.print("  • filesystem - File operations")
            console.print("  • web - Web fetching")
            console.print("  • github - GitHub API (disabled by default)\n")
            console.print("[dim]Edit the configuration file to customize servers.[/dim]\n")
            return

        # Add new server
        if add:
            if not command:
                console.print("[red]Error: --command is required when adding a server[/red]")
                raise typer.Exit(1)

            server = MCPServer(
                name=add,
                command=command.split()[0],
                args=command.split()[1:] if len(command.split()) > 1 else [],
                description="Custom MCP server",
                enabled=True,
            )
            client.add_server(server)
            console.print(f"\n✨ [bold green]Added MCP server:[/bold green] {add}\n")
            return

        # Remove server
        if remove:
            if remove not in client.servers:
                console.print(f"[red]Server not found: {remove}[/red]")
                raise typer.Exit(1)

            client.remove_server(remove)
            console.print(f"\n✨ [bold green]Removed MCP server:[/bold green] {remove}\n")
            return

        # Show tools from specific server
        if server_tools:
            if server_tools not in client.servers:
                console.print(f"[red]Server not found: {server_tools}[/red]")
                raise typer.Exit(1)

            tools = client.get_server_tools(server_tools)

            if not tools:
                console.print(f"[yellow]No tools available from server: {server_tools}[/yellow]")
                return

            table = Table(title=f"Tools from '{server_tools}'", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Category", style="green")
            table.add_column("Description", style="white")

            for tool_def in tools:
                desc = tool_def.description[:60] + "..." if len(tool_def.description) > 60 else tool_def.description
                table.add_row(tool_def.name, tool_def.category, desc)

            console.print("\n")
            console.print(table)
            console.print(f"\n[bold]Total tools:[/bold] {len(tools)}\n")
            return

        # List servers (default)
        servers = client.list_servers()

        if not servers:
            console.print("[yellow]No MCP servers configured.[/yellow]")
            console.print("[dim]Use --init to create example configuration[/dim]\n")
            return

        table = Table(title="MCP Servers", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white")

        for server in servers:
            status = "✓ enabled" if server.enabled else "✗ disabled"
            cmd = f"{server.command} {' '.join(server.args)}"[:40]
            desc = server.description[:40] + "..." if len(server.description) > 40 else server.description
            table.add_row(server.name, cmd, status, desc)

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold]Total servers:[/bold] {len(servers)}")
        console.print(f"[dim]Config: {client.config_path}[/dim]")
        console.print("[dim]Use --server-tools <name> to see available tools[/dim]\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def state(
    list_runs: bool = typer.Option(False, "--list", "-l", help="List all execution runs"),
    show_run: Optional[str] = typer.Option(None, "--show", "-s", help="Show specific run details"),
    weave: Optional[str] = typer.Option(None, "--weave", "-w", help="Filter by weave name"),
    status_filter: Optional[str] = typer.Option(None, "--status", help="Filter by status"),
    latest: bool = typer.Option(False, "--latest", help="Show latest run"),
    cleanup: bool = typer.Option(False, "--cleanup", help="Clean up old state (30 days)"),
    unlock: bool = typer.Option(False, "--unlock", help="Force release lock file"),
    config: Path = typer.Option(".weave.yaml", "--config", "-c", help="Path to config file"),
) -> None:
    """
    Manage execution state and lock files.

    View run history, check status, and manage locks.
    """
    try:
        from ..state.manager import StateManager
        from rich.table import Table
        from datetime import datetime

        # Load config to get state file path
        try:
            weave_config = load_config_from_path(config)
            if weave_config.storage:
                state_file = weave_config.storage.state_file
                lock_file = weave_config.storage.lock_file
            else:
                state_file = ".agent/state.yaml"
                lock_file = ".agent/weave.lock"
        except Exception:
            state_file = ".agent/state.yaml"
            lock_file = ".agent/weave.lock"

        manager = StateManager(state_file=state_file, lock_file=lock_file)

        # Force unlock
        if unlock:
            if manager.release_lock():
                console.print("✅ [green]Lock released successfully[/green]")
            else:
                console.print("ℹ️  [yellow]No lock file found[/yellow]")
            return

        # Cleanup old state
        if cleanup:
            deleted = manager.cleanup_old_states(retention_days=30)
            console.print(f"✅ [green]Cleaned up {deleted} old state(s)[/green]")
            return

        # Show latest run
        if latest:
            state_obj = manager.get_latest_state(weave_name=weave)
            if not state_obj:
                console.print("[yellow]No execution history found[/yellow]")
                return

            console.print(f"\n[bold]Latest Run: {state_obj.run_id}[/bold]\n")
            console.print(f"Weave: {state_obj.weave_name}")
            console.print(f"Status: {state_obj.status}")
            console.print(f"Started: {datetime.fromtimestamp(state_obj.start_time)}")
            if state_obj.end_time:
                console.print(f"Ended: {datetime.fromtimestamp(state_obj.end_time)}")
            console.print(f"Duration: {state_obj.duration:.1f}s" if state_obj.duration else "In progress")
            console.print(f"Agents: {state_obj.completed_agents}/{state_obj.total_agents} completed")
            if state_obj.failed_agents > 0:
                console.print(f"Failed: {state_obj.failed_agents}")
            console.print()
            return

        # Show specific run
        if show_run:
            state_obj = manager.load_state(show_run)
            if not state_obj:
                console.print(f"[red]Run not found: {show_run}[/red]")
                raise typer.Exit(1)

            console.print(f"\n[bold]Run Details: {state_obj.run_id}[/bold]\n")
            console.print(f"Weave: {state_obj.weave_name}")
            console.print(f"Status: {state_obj.status}")
            console.print(f"Started: {datetime.fromtimestamp(state_obj.start_time)}")
            if state_obj.end_time:
                console.print(f"Ended: {datetime.fromtimestamp(state_obj.end_time)}")
            console.print(f"Duration: {state_obj.duration:.1f}s" if state_obj.duration else "In progress")

            # Agent status table
            table = Table(title="Agent Execution Status", show_header=True, header_style="bold magenta")
            table.add_column("Agent", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Duration", style="yellow")
            table.add_column("Tokens", style="blue")

            for agent_name, record in state_obj.agents.items():
                duration_str = f"{record.duration:.1f}s" if record.duration else "N/A"
                tokens_str = str(record.tokens_used) if record.tokens_used else "N/A"
                table.add_row(agent_name, record.status, duration_str, tokens_str)

            console.print("\n")
            console.print(table)
            console.print()
            return

        # List all runs (default)
        runs = manager.list_runs(weave_name=weave, status=status_filter)

        if not runs:
            console.print("[yellow]No execution runs found[/yellow]")
            if weave or status_filter:
                console.print("[dim]Try removing filters[/dim]")
            return

        table = Table(title="Execution Runs", show_header=True, header_style="bold magenta")
        table.add_column("Run ID", style="cyan")
        table.add_column("Weave", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Started", style="blue")
        table.add_column("Duration", style="white")
        table.add_column("Agents", style="magenta")

        for run in runs[:20]:  # Limit to 20 most recent
            started = datetime.fromtimestamp(run.start_time).strftime("%Y-%m-%d %H:%M:%S")
            duration = f"{run.duration:.1f}s" if run.duration else "In progress"
            agents_str = f"{run.completed_agents}/{run.total_agents}"
            if run.failed_agents > 0:
                agents_str += f" ({run.failed_agents} failed)"

            table.add_row(
                run.run_id,
                run.weave_name,
                run.status,
                started,
                duration,
                agents_str
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Showing {min(len(runs), 20)} of {len(runs)} total runs[/dim]")
        console.print("[dim]Use --show <run_id> to view details[/dim]\n")

        # Show lock status
        if manager.is_locked():
            lock = manager.read_lock()
            console.print(f"[yellow]⚠️  Currently locked by run: {lock.run_id}[/yellow]")
            console.print(f"[dim]Use --unlock to force release[/dim]\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def dev(
    config: Path = typer.Option(
        ".agent.yaml", "--config", "-c", help="Path to config file"
    ),
    weave: Optional[str] = typer.Option(
        None, "--weave", "-w", help="Specific weave to run"
    ),
    watch: bool = typer.Option(
        False, "--watch", help="Watch for file changes and auto-reload"
    ),
    real: bool = typer.Option(
        False, "--real", help="Use real LLM execution"
    ),
) -> None:
    """
    Development mode for iterative workflow development.

    Runs the weave and optionally watches for config changes.
    """
    try:
        import asyncio
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class ConfigChangeHandler(FileSystemEventHandler):
            def __init__(self, config_path, weave_name):
                self.config_path = config_path
                self.weave_name = weave_name
                self.last_run = 0

            def on_modified(self, event):
                if event.src_path.endswith(str(self.config_path)):
                    # Debounce: only run if >1 second since last run
                    import time
                    now = time.time()
                    if now - self.last_run < 1:
                        return
                    self.last_run = now

                    console.print("\n[yellow]📝 Config changed, reloading...[/yellow]\n")
                    run_weave(self.config_path, self.weave_name)

        def run_weave(config_path, weave_name_override):
            try:
                # Load config
                weave_config = load_config_from_path(config_path)

                # Determine weave
                if weave_name_override:
                    if weave_name_override not in weave_config.weaves:
                        console.print(f"[red]Weave '{weave_name_override}' not found[/red]")
                        return
                    weave_name = weave_name_override
                else:
                    weave_name = list(weave_config.weaves.keys())[0]

                # Build and execute
                graph = DependencyGraph(weave_config)
                graph.build(weave_name)
                graph.validate()

                from ..runtime.executor import Executor
                executor = Executor(console=console, verbose=True, config=weave_config)
                asyncio.run(executor.execute_flow(graph, weave_name, dry_run=False))

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        # Initial run
        console.print("[bold cyan]🔧 Development Mode[/bold cyan]\n")
        run_weave(config, weave)

        if watch:
            console.print("\n[dim]👀 Watching for changes... (Ctrl+C to stop)[/dim]\n")

            event_handler = ConfigChangeHandler(config, weave)
            observer = Observer()
            observer.schedule(event_handler, str(config.parent), recursive=False)
            observer.start()

            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                console.print("\n[dim]Stopped watching[/dim]\n")
            observer.join()

    except ImportError:
        console.print("[red]watchdog not installed. Run: pip install watchdog[/red]")
        raise typer.Exit(1)
    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def inspect(
    run_id: str = typer.Argument(..., help="Run ID to inspect"),
    config: Path = typer.Option(
        ".agent.yaml", "--config", "-c", help="Path to config file"
    ),
    show_prompts: bool = typer.Option(
        False, "--prompts", help="Show LLM prompts sent"
    ),
    show_outputs: bool = typer.Option(
        True, "--outputs/--no-outputs", help="Show agent outputs"
    ),
    show_tools: bool = typer.Option(
        True, "--tools/--no-tools", help="Show tool calls"
    ),
) -> None:
    """
    Inspect a completed run in detail.

    Shows full execution trace, agent I/O, tool calls, and metrics.
    """
    try:
        from ..state.manager import StateManager
        from rich.table import Table
        from rich.panel import Panel
        from rich.syntax import Syntax
        from datetime import datetime
        import json

        # Load config to get state file path
        try:
            weave_config = load_config_from_path(config)
            if weave_config.storage:
                state_file = weave_config.storage.state_file
            else:
                state_file = ".agent/state.yaml"
        except Exception:
            state_file = ".agent/state.yaml"

        manager = StateManager(state_file=state_file)

        # Load state
        state = manager.load_state(run_id)
        if not state:
            console.print(f"[red]Run not found: {run_id}[/red]")
            console.print("[dim]Use 'weave state --list' to see available runs[/dim]")
            raise typer.Exit(1)

        # Display run overview
        console.print(f"\n[bold]Run Inspection: {run_id}[/bold]\n")

        overview = Table.grid(padding=(0, 2))
        overview.add_column(style="cyan")
        overview.add_column()

        overview.add_row("Weave:", state.weave_name)
        overview.add_row("Status:", f"[green]{state.status}[/green]" if state.status == "completed" else f"[red]{state.status}[/red]")
        overview.add_row("Started:", datetime.fromtimestamp(state.start_time).strftime("%Y-%m-%d %H:%M:%S"))
        if state.end_time:
            overview.add_row("Ended:", datetime.fromtimestamp(state.end_time).strftime("%Y-%m-%d %H:%M:%S"))
        overview.add_row("Duration:", f"{state.duration:.2f}s" if state.duration else "In progress")
        overview.add_row("Agents:", f"{state.completed_agents}/{state.total_agents} completed")
        if state.failed_agents > 0:
            overview.add_row("Failed:", f"[red]{state.failed_agents}[/red]")

        console.print(overview)
        console.print()

        # Display agent execution details
        console.print("[bold]Agent Execution Details[/bold]\n")

        for agent_name, record in state.agents.items():
            status_icon = "✓" if record.status == "success" else "✗"
            status_color = "green" if record.status == "success" else "red"

            header = f"{status_icon} [{status_color}]{agent_name}[/{status_color}]"
            if record.duration:
                header += f" [dim]({record.duration:.2f}s, {record.tokens_used} tokens)[/dim]"

            console.print(header)

            if show_outputs and record.output:
                # Display output
                if isinstance(record.output, dict):
                    output_json = json.dumps(record.output, indent=2)
                    syntax = Syntax(output_json, "json", theme="monokai", line_numbers=False)
                    console.print(Panel(syntax, title="Output", border_style="dim"))
                else:
                    console.print(Panel(str(record.output), title="Output", border_style="dim"))

            console.print()

        console.print("[dim]Tip: Use --no-outputs to hide output details[/dim]\n")

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


@app.command()
def run(
    agent: str = typer.Argument(..., help="Agent name from config"),
    config: Path = typer.Option(
        ".agent.yaml", "--config", "-c", help="Path to config file"
    ),
    openai_mode: bool = typer.Option(
        False, "--openai-mode", help="Run as OpenAI-compatible API server"
    ),
    host: str = typer.Option(
        "0.0.0.0", "--host", help="Host to bind to (OpenAI mode only)"
    ),
    port: int = typer.Option(
        8000, "--port", help="Port to bind to (OpenAI mode only)"
    ),
) -> None:
    """
    Run an interactive agentic chat session or OpenAI-compatible API server.

    Start a conversational interface with an AI agent from your config,
    or run as a headless OpenAI-compatible API endpoint with --openai-mode.
    """
    try:
        # Handle OpenAI mode
        if openai_mode:
            try:
                from ..api.openai_server import start_openai_server
            except ImportError:
                console.print(
                    "[red]Error:[/red] FastAPI and uvicorn are required for OpenAI mode.\n"
                    "[dim]Install with:[/dim] pip install 'weave-cli[api]'\n"
                )
                raise typer.Exit(1)

            start_openai_server(
                agent_name=agent,
                config_path=config,
                host=host,
                port=port,
                verbose=True
            )
            return

        # Interactive mode (original behavior)
        import asyncio
        from ..runtime.llm_executor import LLMExecutor
        from ..core.sessions import ConversationSession
        import uuid

        console.print("\n[bold cyan]🤖 Weave Agentic Chat[/bold cyan]")
        console.print("[dim]Type 'exit' or 'quit' to end the session[/dim]\n")

        # Load config and agent
        weave_config = load_config_from_path(config)
        if agent not in weave_config.agents:
            available = ", ".join(weave_config.agents.keys())
            console.print(f"[red]Agent '{agent}' not found.[/red]")
            console.print(f"[dim]Available agents: {available}[/dim]\n")
            raise typer.Exit(1)

        agent_obj = weave_config.agents[agent]
        console.print(f"[green]Using agent:[/green] {agent}")
        console.print(f"[dim]Model: {agent_obj.model}[/dim]\n")

        # Create session
        session_id = str(uuid.uuid4())[:8]
        session = ConversationSession(
            session_id=session_id,
            weave_name="chat",
            agent_name=agent_obj.name
        )

        # Initialize executor
        executor = LLMExecutor(
            console=console,
            verbose=False,
            config=weave_config,
            session=session
        )

        # Chat loop
        async def chat_loop():
            while True:
                try:
                    # Get user input
                    user_input = console.input("\n[bold cyan]You:[/bold cyan] ")

                    if not user_input.strip():
                        continue

                    if user_input.lower() in ['exit', 'quit', 'q']:
                        console.print("\n[dim]Goodbye! 👋[/dim]\n")
                        break

                    # Execute agent
                    context = {"task": user_input}
                    response = await executor.execute_agent(agent_obj, context)

                    # Display response
                    console.print(f"\n[bold green]Assistant:[/bold green] {response.content}")

                except KeyboardInterrupt:
                    console.print("\n\n[dim]Goodbye! 👋[/dim]\n")
                    break
                except Exception as e:
                    console.print(f"\n[red]Error:[/red] {e}\n")

        asyncio.run(chat_loop())

    except Exception as e:
        output.print_error(e)
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
