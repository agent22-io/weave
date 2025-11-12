"""Built-in tools for Weave agents."""

from typing import Any, Dict, List
import json
import os
from pathlib import Path

from weave.tools.models import Tool, ToolDefinition, ToolParameter, ParameterType


def calculator(expression: str) -> Dict[str, Any]:
    """Evaluate a mathematical expression."""
    try:
        # Safe evaluation using ast
        import ast
        import operator

        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)

        result = eval_expr(ast.parse(expression, mode="eval").body)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}


def text_length(text: str) -> Dict[str, Any]:
    """Count characters, words, and lines in text."""
    lines = text.split("\n")
    words = text.split()

    return {
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
        "text_preview": text[:100] + ("..." if len(text) > 100 else ""),
    }


def json_validator(json_string: str) -> Dict[str, Any]:
    """Validate and parse JSON string."""
    try:
        parsed = json.loads(json_string)
        return {
            "valid": True,
            "parsed": parsed,
            "type": type(parsed).__name__,
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e),
            "line": e.lineno,
            "column": e.colno,
        }


def string_formatter(
    template: str, variables: Dict[str, Any], format_type: str = "format"
) -> Dict[str, Any]:
    """Format strings with variables."""
    try:
        if format_type == "format":
            result = template.format(**variables)
        elif format_type == "template":
            from string import Template

            result = Template(template).substitute(variables)
        else:
            return {"error": f"Unknown format type: {format_type}"}

        return {"result": result, "template": template, "variables": variables}
    except Exception as e:
        return {"error": str(e), "template": template}


def list_operations(
    operation: str, items: List[Any], value: Any = None
) -> Dict[str, Any]:
    """Perform operations on lists."""
    try:
        if operation == "append":
            items.append(value)
            return {"result": items, "operation": "append"}
        elif operation == "count":
            return {"result": len(items), "operation": "count"}
        elif operation == "sum" and all(isinstance(x, (int, float)) for x in items):
            return {"result": sum(items), "operation": "sum"}
        elif operation == "sort":
            return {"result": sorted(items), "operation": "sort"}
        elif operation == "reverse":
            return {"result": list(reversed(items)), "operation": "reverse"}
        elif operation == "unique":
            return {"result": list(set(items)), "operation": "unique"}
        else:
            return {"error": f"Unknown operation: {operation}"}
    except Exception as e:
        return {"error": str(e), "operation": operation}


def http_request(
    url: str, method: str = "GET", headers: Dict[str, str] = None,
    body: str = None, timeout: int = 30
) -> Dict[str, Any]:
    """Make HTTP requests."""
    try:
        import requests

        method = method.upper()
        headers = headers or {}

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=body, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, data=body, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, data=body, timeout=timeout)
        else:
            return {"error": f"Unsupported HTTP method: {method}"}

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "url": url,
            "method": method,
        }
    except ImportError:
        return {"error": "requests library required. Install: pip install requests"}
    except Exception as e:
        return {"error": str(e), "url": url, "method": method}


def file_read(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read file contents."""
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        if not path.is_file():
            return {"error": f"Not a file: {file_path}"}

        content = path.read_text(encoding=encoding)

        return {
            "content": content,
            "path": str(path),
            "size": len(content),
            "lines": len(content.splitlines()),
        }
    except Exception as e:
        return {"error": str(e), "path": file_path}


def file_write(file_path: str, content: str, encoding: str = "utf-8",
               create_dirs: bool = True) -> Dict[str, Any]:
    """Write content to file."""
    try:
        path = Path(file_path).expanduser().resolve()

        # Create parent directories if needed
        if create_dirs and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding=encoding)

        return {
            "success": True,
            "path": str(path),
            "size": len(content),
            "lines": len(content.splitlines()),
        }
    except Exception as e:
        return {"error": str(e), "path": file_path}


def file_list(directory: str = ".", pattern: str = "*", recursive: bool = False) -> Dict[str, Any]:
    """List files in directory."""
    try:
        path = Path(directory).expanduser().resolve()

        if not path.exists():
            return {"error": f"Directory not found: {directory}"}

        if not path.is_dir():
            return {"error": f"Not a directory: {directory}"}

        if recursive:
            files = [str(p.relative_to(path)) for p in path.rglob(pattern) if p.is_file()]
            dirs = [str(p.relative_to(path)) for p in path.rglob(pattern) if p.is_dir()]
        else:
            files = [p.name for p in path.glob(pattern) if p.is_file()]
            dirs = [p.name for p in path.glob(pattern) if p.is_dir()]

        return {
            "directory": str(path),
            "files": sorted(files),
            "directories": sorted(dirs),
            "total_files": len(files),
            "total_directories": len(dirs),
        }
    except Exception as e:
        return {"error": str(e), "directory": directory}


def bash_execute(command: str, timeout: int = 30, working_dir: str = None) -> Dict[str, Any]:
    """Execute a bash command."""
    try:
        import subprocess

        # Set working directory
        cwd = Path(working_dir).expanduser().resolve() if working_dir else None

        # Validate working directory if specified
        if cwd and not cwd.exists():
            return {"error": f"Working directory not found: {working_dir}"}

        if cwd and not cwd.is_dir():
            return {"error": f"Not a directory: {working_dir}"}

        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )

        return {
            "command": command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "working_dir": str(cwd) if cwd else os.getcwd(),
        }
    except subprocess.TimeoutExpired:
        return {
            "error": f"Command timed out after {timeout} seconds",
            "command": command,
            "timeout": timeout,
        }
    except Exception as e:
        return {
            "error": str(e),
            "command": command,
        }


def get_builtin_tools() -> List[Tool]:
    """Get all built-in tools.

    Returns:
        List of built-in Tool instances
    """
    return [
        Tool(
            definition=ToolDefinition(
                name="calculator",
                description="Evaluate mathematical expressions safely",
                parameters=[
                    ToolParameter(
                        name="expression",
                        type=ParameterType.STRING,
                        description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')",
                        required=True,
                    )
                ],
                category="math",
                tags=["calculator", "math", "arithmetic"],
            ),
            handler=calculator,
        ),
        Tool(
            definition=ToolDefinition(
                name="text_length",
                description="Count characters, words, and lines in text",
                parameters=[
                    ToolParameter(
                        name="text",
                        type=ParameterType.STRING,
                        description="Text to analyze",
                        required=True,
                    )
                ],
                category="text",
                tags=["text", "analysis", "statistics"],
            ),
            handler=text_length,
        ),
        Tool(
            definition=ToolDefinition(
                name="json_validator",
                description="Validate and parse JSON strings",
                parameters=[
                    ToolParameter(
                        name="json_string",
                        type=ParameterType.STRING,
                        description="JSON string to validate and parse",
                        required=True,
                    )
                ],
                category="data",
                tags=["json", "validation", "parsing"],
            ),
            handler=json_validator,
        ),
        Tool(
            definition=ToolDefinition(
                name="string_formatter",
                description="Format strings using template variables",
                parameters=[
                    ToolParameter(
                        name="template",
                        type=ParameterType.STRING,
                        description="String template (e.g., 'Hello {name}')",
                        required=True,
                    ),
                    ToolParameter(
                        name="variables",
                        type=ParameterType.OBJECT,
                        description="Variables to substitute in template",
                        required=True,
                    ),
                    ToolParameter(
                        name="format_type",
                        type=ParameterType.STRING,
                        description="Format type: 'format' or 'template'",
                        required=False,
                        default="format",
                        enum=["format", "template"],
                    ),
                ],
                category="text",
                tags=["string", "formatting", "template"],
            ),
            handler=string_formatter,
        ),
        Tool(
            definition=ToolDefinition(
                name="list_operations",
                description="Perform operations on lists (append, count, sum, sort, reverse, unique)",
                parameters=[
                    ToolParameter(
                        name="operation",
                        type=ParameterType.STRING,
                        description="Operation to perform",
                        required=True,
                        enum=["append", "count", "sum", "sort", "reverse", "unique"],
                    ),
                    ToolParameter(
                        name="items",
                        type=ParameterType.ARRAY,
                        description="List of items",
                        required=True,
                    ),
                    ToolParameter(
                        name="value",
                        type=ParameterType.STRING,
                        description="Value for operations like append",
                        required=False,
                    ),
                ],
                category="data",
                tags=["list", "array", "operations"],
            ),
            handler=list_operations,
        ),
        Tool(
            definition=ToolDefinition(
                name="http_request",
                description="Make HTTP requests (GET, POST, PUT, DELETE, PATCH)",
                parameters=[
                    ToolParameter(
                        name="url",
                        type=ParameterType.STRING,
                        description="URL to request",
                        required=True,
                    ),
                    ToolParameter(
                        name="method",
                        type=ParameterType.STRING,
                        description="HTTP method",
                        required=False,
                        default="GET",
                        enum=["GET", "POST", "PUT", "DELETE", "PATCH"],
                    ),
                    ToolParameter(
                        name="headers",
                        type=ParameterType.OBJECT,
                        description="HTTP headers",
                        required=False,
                    ),
                    ToolParameter(
                        name="body",
                        type=ParameterType.STRING,
                        description="Request body",
                        required=False,
                    ),
                    ToolParameter(
                        name="timeout",
                        type=ParameterType.NUMBER,
                        description="Request timeout in seconds",
                        required=False,
                        default=30,
                    ),
                ],
                category="web",
                tags=["http", "api", "web", "request"],
            ),
            handler=http_request,
        ),
        Tool(
            definition=ToolDefinition(
                name="file_read",
                description="Read file contents",
                parameters=[
                    ToolParameter(
                        name="file_path",
                        type=ParameterType.STRING,
                        description="Path to file",
                        required=True,
                    ),
                    ToolParameter(
                        name="encoding",
                        type=ParameterType.STRING,
                        description="File encoding",
                        required=False,
                        default="utf-8",
                    ),
                ],
                category="filesystem",
                tags=["file", "read", "io"],
            ),
            handler=file_read,
        ),
        Tool(
            definition=ToolDefinition(
                name="file_write",
                description="Write content to file",
                parameters=[
                    ToolParameter(
                        name="file_path",
                        type=ParameterType.STRING,
                        description="Path to file",
                        required=True,
                    ),
                    ToolParameter(
                        name="content",
                        type=ParameterType.STRING,
                        description="Content to write",
                        required=True,
                    ),
                    ToolParameter(
                        name="encoding",
                        type=ParameterType.STRING,
                        description="File encoding",
                        required=False,
                        default="utf-8",
                    ),
                    ToolParameter(
                        name="create_dirs",
                        type=ParameterType.BOOLEAN,
                        description="Create parent directories if they don't exist",
                        required=False,
                        default=True,
                    ),
                ],
                category="filesystem",
                tags=["file", "write", "io"],
            ),
            handler=file_write,
        ),
        Tool(
            definition=ToolDefinition(
                name="file_list",
                description="List files in directory",
                parameters=[
                    ToolParameter(
                        name="directory",
                        type=ParameterType.STRING,
                        description="Directory path",
                        required=False,
                        default=".",
                    ),
                    ToolParameter(
                        name="pattern",
                        type=ParameterType.STRING,
                        description="File pattern (glob)",
                        required=False,
                        default="*",
                    ),
                    ToolParameter(
                        name="recursive",
                        type=ParameterType.BOOLEAN,
                        description="Search recursively",
                        required=False,
                        default=False,
                    ),
                ],
                category="filesystem",
                tags=["file", "list", "directory"],
            ),
            handler=file_list,
        ),
        Tool(
            definition=ToolDefinition(
                name="bash_execute",
                description="Execute bash commands and return output",
                parameters=[
                    ToolParameter(
                        name="command",
                        type=ParameterType.STRING,
                        description="Bash command to execute",
                        required=True,
                    ),
                    ToolParameter(
                        name="timeout",
                        type=ParameterType.NUMBER,
                        description="Command timeout in seconds",
                        required=False,
                        default=30,
                    ),
                    ToolParameter(
                        name="working_dir",
                        type=ParameterType.STRING,
                        description="Working directory for command execution",
                        required=False,
                    ),
                ],
                category="system",
                tags=["bash", "shell", "command", "execute"],
            ),
            handler=bash_execute,
        ),
    ]
