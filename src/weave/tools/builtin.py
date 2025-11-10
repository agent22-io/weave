"""Built-in tools for Weave agents."""

from typing import Any, Dict, List
import json

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
    ]
