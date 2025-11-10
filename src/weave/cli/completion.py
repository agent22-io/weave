"""Shell completion generation for Weave CLI."""

import os
from pathlib import Path
from typing import Optional

from rich.console import Console


def get_shell_config_file(shell: str) -> Optional[Path]:
    """Get the config file path for a shell.

    Args:
        shell: Shell name (bash, zsh, fish)

    Returns:
        Path to shell config file
    """
    home = Path.home()

    if shell == "bash":
        # Try .bashrc first, then .bash_profile
        if (home / ".bashrc").exists():
            return home / ".bashrc"
        return home / ".bash_profile"
    elif shell == "zsh":
        return home / ".zshrc"
    elif shell == "fish":
        config_dir = home / ".config" / "fish"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.fish"

    return None


def generate_bash_completion() -> str:
    """Generate bash completion script.

    Returns:
        Bash completion script
    """
    return """# Weave CLI bash completion

_weave_completion() {
    local IFS=$'\\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _WEAVE_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_weave_completion_setup() {
    complete -o nosort -F _weave_completion weave
}

_weave_completion_setup;
"""


def generate_zsh_completion() -> str:
    """Generate zsh completion script.

    Returns:
        Zsh completion script
    """
    return """#compdef weave

_weave_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[weave] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _WEAVE_COMPLETE=zsh_complete weave)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _weave_completion weave;
"""


def generate_fish_completion() -> str:
    """Generate fish completion script.

    Returns:
        Fish completion script
    """
    return """# Weave CLI fish completion

function _weave_completion
    set -l response (env _WEAVE_COMPLETE=fish_complete COMP_WORDS=(commandline -opc) COMP_CWORD=(commandline -t) weave)

    for completion in $response
        set -l metadata (string split "," -- $completion)

        if test $metadata[1] = "dir"
            __fish_complete_directories $metadata[2]
        else if test $metadata[1] = "file"
            __fish_complete_path $metadata[2]
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete -f -c weave -a "(_weave_completion)"
"""


def install_completion(shell: str, console: Optional[Console] = None) -> bool:
    """Install shell completion for Weave.

    Args:
        shell: Shell to install for (bash, zsh, fish)
        console: Rich console for output

    Returns:
        True if installed successfully
    """
    if console is None:
        console = Console()

    # Get shell config file
    config_file = get_shell_config_file(shell)
    if not config_file:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return False

    # Generate completion script
    if shell == "bash":
        completion = generate_bash_completion()
    elif shell == "zsh":
        completion = generate_zsh_completion()
    elif shell == "fish":
        completion = generate_fish_completion()
    else:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return False

    # Check if already installed
    if config_file.exists():
        content = config_file.read_text()
        if "weave_completion" in content or "_weave_completion" in content:
            console.print(f"[yellow]Completion already installed in {config_file}[/yellow]")
            return True

    # Add completion to config file
    try:
        with open(config_file, "a") as f:
            f.write("\n# Weave CLI completion\n")
            f.write(completion)

        console.print(f"[green]✓ Installed {shell} completion to {config_file}[/green]")
        console.print(f"\n[dim]Restart your shell or run:[/dim]")
        console.print(f"[cyan]source {config_file}[/cyan]\n")
        return True

    except Exception as e:
        console.print(f"[red]Error installing completion: {e}[/red]")
        return False


def show_completion_script(shell: str, console: Optional[Console] = None) -> None:
    """Show completion script for manual installation.

    Args:
        shell: Shell to show script for
        console: Rich console for output
    """
    if console is None:
        console = Console()

    if shell == "bash":
        script = generate_bash_completion()
    elif shell == "zsh":
        script = generate_zsh_completion()
    elif shell == "fish":
        script = generate_fish_completion()
    else:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return

    console.print(script)
