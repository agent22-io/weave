"""Post-installation setup wizard for Weave CLI."""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table


def run_setup_wizard(console: Optional[Console] = None) -> None:
    """Run interactive setup wizard.

    Args:
        console: Rich console for output
    """
    if console is None:
        console = Console()

    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🧵 Weave CLI Setup Wizard[/bold cyan]\n\n"
        "This wizard will help you configure Weave for first-time use.",
        border_style="cyan"
    ))
    console.print("\n")

    # 1. Create .weave directory
    setup_weave_directory(console)

    # 2. Configure API keys
    setup_api_keys(console)

    # 3. Install shell completion
    setup_shell_completion(console)

    # 4. Create example project
    setup_example_project(console)

    # 5. Show next steps
    show_next_steps(console)


def setup_weave_directory(console: Console) -> None:
    """Create .weave directory structure.

    Args:
        console: Rich console
    """
    console.print("[bold]1. Setting up Weave directory[/bold]\n")

    weave_dir = Path.home() / ".weave"

    if weave_dir.exists():
        console.print(f"[dim]✓ Directory already exists: {weave_dir}[/dim]\n")
        return

    create = Confirm.ask("Create ~/.weave directory for configuration?", default=True)

    if create:
        weave_dir.mkdir(parents=True, exist_ok=True)
        (weave_dir / "state.yaml").touch()
        (weave_dir / "cache").mkdir(exist_ok=True)

        console.print(f"[green]✓ Created {weave_dir}[/green]")
        console.print(f"[green]✓ Created {weave_dir}/state.yaml[/green]")
        console.print(f"[green]✓ Created {weave_dir}/cache/[/green]\n")
    else:
        console.print("[dim]Skipped[/dim]\n")


def setup_api_keys(console: Console) -> None:
    """Configure API keys for LLM providers.

    Args:
        console: Rich console
    """
    console.print("[bold]2. Configure API Keys[/bold]\n")

    console.print("Weave supports multiple LLM providers:")
    console.print("  • OpenAI (GPT-4, GPT-3.5)")
    console.print("  • Anthropic (Claude)")
    console.print("  • OpenRouter (multi-model access)")
    console.print("\n[dim]Keys are stored encrypted in ~/.weave/api_keys.yaml[/dim]")
    console.print("[dim]You can skip this and use environment variables instead.[/dim]\n")

    configure = Confirm.ask("Configure API keys now?", default=False)

    if not configure:
        console.print("[dim]Skipped - you can set these later using environment variables:[/dim]")
        console.print("[dim]  export OPENAI_API_KEY='sk-...'[/dim]")
        console.print("[dim]  export ANTHROPIC_API_KEY='sk-ant-...'[/dim]\n")
        return

    # Use API key manager
    from ..core.api_keys import get_key_manager
    manager = get_key_manager()

    configured_count = 0

    # OpenAI
    if Confirm.ask("Configure OpenAI API key?", default=True):
        api_key = Prompt.ask("Enter your OpenAI API key", password=True)
        if api_key and api_key.strip():
            manager.set_key("openai", api_key.strip())
            console.print("[green]✓ OpenAI API key saved (encrypted)[/green]")
            configured_count += 1

    # Anthropic
    if Confirm.ask("Configure Anthropic API key?", default=False):
        api_key = Prompt.ask("Enter your Anthropic API key", password=True)
        if api_key and api_key.strip():
            manager.set_key("anthropic", api_key.strip())
            console.print("[green]✓ Anthropic API key saved (encrypted)[/green]")
            configured_count += 1

    # OpenRouter
    if Confirm.ask("Configure OpenRouter API key?", default=False):
        api_key = Prompt.ask("Enter your OpenRouter API key", password=True)
        if api_key and api_key.strip():
            manager.set_key("openrouter", api_key.strip())
            console.print("[green]✓ OpenRouter API key saved (encrypted)[/green]")
            configured_count += 1

    if configured_count > 0:
        console.print(f"\n[green]✓ Configured {configured_count} API key(s)[/green]")
        console.print("[dim]Stored encrypted in ~/.weave/api_keys.yaml[/dim]\n")
    else:
        console.print("[dim]No API keys configured[/dim]\n")


def setup_shell_completion(console: Console) -> None:
    """Install shell completion.

    Args:
        console: Rich console
    """
    console.print("[bold]3. Shell Completion[/bold]\n")

    console.print("Shell completion enables tab-completion for Weave commands.\n")

    install = Confirm.ask("Install shell completion?", default=True)

    if not install:
        console.print("[dim]Skipped[/dim]\n")
        return

    # Detect shell
    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell not in ["bash", "zsh", "fish"]:
        console.print(f"[yellow]Could not detect shell. Current: {shell}[/yellow]")
        shell = Prompt.ask(
            "Enter your shell",
            choices=["bash", "zsh", "fish"],
            default="bash"
        )

    console.print(f"\n[dim]Installing completion for {shell}...[/dim]")

    try:
        from .completion import install_completion

        if install_completion(shell, console):
            console.print("[green]✓ Shell completion installed[/green]\n")
        else:
            console.print("[yellow]⚠️  Could not install completion automatically[/yellow]")
            console.print(f"[dim]Run: weave completion --install {shell}[/dim]\n")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]\n")


def setup_example_project(console: Console) -> None:
    """Create example project.

    Args:
        console: Rich console
    """
    console.print("[bold]4. Example Project[/bold]\n")

    if Path(".weave.yaml").exists():
        console.print("[dim]✓ .weave.yaml already exists in current directory[/dim]\n")
        return

    create = Confirm.ask("Create example .weave.yaml in current directory?", default=True)

    if create:
        example_config = """# Weave Configuration
# https://docs.weave.dev

version: "1.0"

agents:
  researcher:
    model: "gpt-4"
    tools:
      - web_search
    outputs: "research_summary"
    prompt: |
      Research the given topic and provide key insights.

  writer:
    model: "claude-3-opus"
    inputs: "researcher"
    outputs: "article"
    prompt: |
      Write a detailed article based on the research findings.

weaves:
  content_pipeline:
    agents:
      - researcher
      - writer
"""
        Path(".weave.yaml").write_text(example_config)
        console.print("[green]✓ Created .weave.yaml[/green]")
        console.print("[dim]You can now run: weave apply[/dim]\n")
    else:
        console.print("[dim]Skipped[/dim]\n")


def show_next_steps(console: Console) -> None:
    """Show next steps after setup.

    Args:
        console: Rich console
    """
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]✨ Setup Complete![/bold green]",
        border_style="green"
    ))
    console.print("\n")

    console.print("[bold]Next Steps:[/bold]\n")

    steps = Table(show_header=False, box=None, padding=(0, 2))
    steps.add_column(style="cyan")
    steps.add_column(style="white")

    steps.add_row("1.", "Test the installation:")
    steps.add_row("", "[dim]weave --version[/dim]")
    steps.add_row("", "")
    steps.add_row("2.", "View help:")
    steps.add_row("", "[dim]weave --help[/dim]")
    steps.add_row("", "")
    steps.add_row("3.", "Try an example:")
    steps.add_row("", "[dim]weave apply[/dim]")
    steps.add_row("", "")
    steps.add_row("4.", "Run with real LLMs:")
    steps.add_row("", "[dim]weave apply --real[/dim]")
    steps.add_row("", "")
    steps.add_row("5.", "Development mode with auto-reload:")
    steps.add_row("", "[dim]weave dev --watch[/dim]")

    console.print(steps)
    console.print("\n")

    console.print("[bold]Resources:[/bold]\n")
    console.print("  📚 Documentation: https://docs.weave.dev")
    console.print("  💬 Community: https://github.com/weave/weave-cli")
    console.print("  🐛 Issues: https://github.com/weave/weave-cli/issues")
    console.print("\n")


def check_installation(console: Optional[Console] = None) -> None:
    """Check installation and show status.

    Args:
        console: Rich console for output
    """
    if console is None:
        console = Console()

    console.print("\n[bold]Weave Installation Status[/bold]\n")

    checks = Table(show_header=True)
    checks.add_column("Component", style="cyan")
    checks.add_column("Status", style="white")
    checks.add_column("Notes", style="dim")

    # Check core installation
    try:
        from .. import __version__
        checks.add_row("Core", "[green]✓ Installed[/green]", f"v{__version__}")
    except:
        checks.add_row("Core", "[red]✗ Not found[/red]", "")

    # Check optional dependencies
    optional_deps = {
        "OpenAI": "openai",
        "Anthropic": "anthropic",
        "Watchdog": "watchdog",
        "Boto3 (AWS)": "boto3",
        "Docker": "docker",
    }

    for name, module in optional_deps.items():
        try:
            __import__(module)
            checks.add_row(name, "[green]✓ Installed[/green]", "")
        except ImportError:
            checks.add_row(name, "[dim]- Not installed[/dim]", "Optional")

    # Check configuration
    weave_dir = Path.home() / ".weave"
    if weave_dir.exists():
        checks.add_row("Config Dir", "[green]✓ Exists[/green]", str(weave_dir))
    else:
        checks.add_row("Config Dir", "[yellow]⚠ Missing[/yellow]", "Run: weave setup")

    # Check API keys (both config and env vars)
    from ..core.api_keys import get_key_manager
    manager = get_key_manager()

    openai_key = manager.get_key("openai")
    if openai_key:
        source = "env var" if os.getenv("OPENAI_API_KEY") else "config"
        checks.add_row("OpenAI Key", "[green]✓ Set[/green]", source)
    else:
        checks.add_row("OpenAI Key", "[dim]- Not set[/dim]", "")

    anthropic_key = manager.get_key("anthropic")
    if anthropic_key:
        source = "env var" if os.getenv("ANTHROPIC_API_KEY") else "config"
        checks.add_row("Anthropic Key", "[green]✓ Set[/green]", source)
    else:
        checks.add_row("Anthropic Key", "[dim]- Not set[/dim]", "")

    console.print(checks)
    console.print("\n")

    # Recommendations
    console.print("[bold]Recommendations:[/bold]\n")

    if not weave_dir.exists():
        console.print("  • Run [cyan]weave setup[/cyan] to configure Weave")

    if not openai_key and not anthropic_key:
        console.print("  • Set API keys for real LLM execution:")
        console.print("    [dim]export OPENAI_API_KEY='sk-...'[/dim]")
        console.print("    [dim]export ANTHROPIC_API_KEY='sk-ant-...'[/dim]")

    try:
        __import__("openai")
    except ImportError:
        console.print("  • Install LLM support: [cyan]pip install weave-cli[llm][/cyan]")

    console.print("\n")
