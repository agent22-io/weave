"""Execution engine with LLM, plugin, and tool integration."""

import time
import asyncio
import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from ..core.graph import DependencyGraph
from ..core.models import Agent, WeaveConfig
from ..core.memory import MemoryManager
from .llm_executor import LLMExecutor
from .hooks import ExecutorHook


@dataclass
class AgentOutput:
    """Output from an agent execution."""
    agent_name: str
    output_key: str
    data: Any
    execution_time: float
    status: str = "success"
    tokens_used: int = 0
    metadata: Dict[str, Any] = None

    # Backward compatibility
    @property
    def output(self) -> Any:
        """Alias for data field."""
        return self.data


@dataclass
class ExecutionSummary:
    """Summary of workflow execution."""
    weave_name: str
    total_agents: int
    successful: int
    failed: int
    total_time: float
    total_tokens: int = 0
    outputs: Dict[str, Any] = None


class Executor:
    """
    Agent execution engine with LLM, tool, and plugin support.

    Features:
    - Actual LLM API calls (OpenAI, Anthropic)
    - Plugin execution during agent runs
    - Tool calling with MCP integration
    - State management and storage
    - Retry logic and error handling
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        verbose: bool = False,
        config: Optional[WeaveConfig] = None,
        session: Optional["ConversationSession"] = None,
        session_id: Optional[str] = None,
    ):
        """Initialize executor.

        Args:
            console: Rich console for output
            verbose: Enable verbose logging
            config: Weave configuration
            session: Existing conversation session to continue
            session_id: Session ID for saving conversation
        """
        self.console = console or Console()
        self.verbose = verbose
        self.config = config
        self.outputs: Dict[str, AgentOutput] = {}
        self.run_id = str(uuid.uuid4())[:8]

        # Hook management
        self.hooks: List[ExecutorHook] = []

        # Session management
        self.session = session
        self.session_id = session_id
        if session_id and not session:
            # Create new session
            from ..core.sessions import ConversationSession
            self.session = ConversationSession(
                session_id=session_id,
                weave_name=None,  # Will be set during execution
                agent_name=None,
            )

        # Initialize resource loader
        self._initialize_resources()

        # Initialize LLM executor with session (memory manager will be set per agent)
        self.llm_executor = LLMExecutor(
            console=self.console,
            verbose=self.verbose,
            config=self.config,
            session=self.session,
            resource_loader=self.resource_loader,
        )
        self.memory_managers: Dict[str, MemoryManager] = {}

        # Initialize systems
        self._initialize_tools()
        self._initialize_plugins()
        self._initialize_state_management()
        self._initialize_storage()

    def register_hook(self, hook: ExecutorHook) -> None:
        """
        Register a hook to be called during agent execution.

        Hooks are called before and after each agent execution, allowing
        custom logging, metrics collection, notifications, and more.

        Args:
            hook: Hook instance implementing ExecutorHook protocol

        Example:
            executor = Executor()
            executor.register_hook(LoggingHook("weave.log"))
            executor.register_hook(MetricsHook())
        """
        if not isinstance(hook, ExecutorHook):
            # Try to verify it at least has the right methods
            if not (hasattr(hook, "before_agent") and hasattr(hook, "after_agent")):
                raise TypeError(
                    f"Hook must implement ExecutorHook protocol with "
                    f"before_agent() and after_agent() methods. Got: {type(hook)}"
                )

        self.hooks.append(hook)
        if self.verbose:
            self.console.print(
                f"[dim]Registered hook: {type(hook).__name__}[/dim]"
            )

    def _initialize_resources(self) -> None:
        """Initialize resource loader for agent resources."""
        try:
            from ..resources.loader import ResourceLoader
            from pathlib import Path

            # Use .agent/ directory in current working directory
            base_path = Path(".weave")
            self.resource_loader = ResourceLoader(base_path)

            # Load all resources if .weave directory exists
            if base_path.exists():
                self.resource_loader.load_all()
                if self.verbose:
                    resources = self.resource_loader.list_resources()
                    total = sum(len(r) for r in resources.values())
                    self.console.print(f"[dim]Loaded {total} resources[/dim]")
            else:
                if self.verbose:
                    self.console.print("[dim]No .agent/ directory found, resources disabled[/dim]")

        except ImportError as e:
            if self.verbose:
                self.console.print(f"[yellow]Resource system not available: {e}[/yellow]")
            self.resource_loader = None

    def _initialize_tools(self) -> None:
        """Initialize tool executor with custom tools and MCP."""
        try:
            from ..tools.executor import ToolExecutor
            from ..tools.mcp_client import MCPClient

            self.tool_executor = ToolExecutor()

            # Load MCP servers if configured
            if self.config and self.config.mcp_servers:
                self.mcp_client = MCPClient(weave_config=self.config)
                if self.verbose:
                    enabled = [
                        name
                        for name, server in self.mcp_client.servers.items()
                        if server.enabled
                    ]
                    self.console.print(
                        f"[dim]Loaded {len(enabled)} MCP servers: {', '.join(enabled)}[/dim]"
                    )
            else:
                self.mcp_client = None

        except ImportError as e:
            if self.verbose:
                self.console.print(f"[yellow]Tool system not available: {e}[/yellow]")
            self.tool_executor = None
            self.mcp_client = None

    def _initialize_plugins(self) -> None:
        """Initialize plugin manager."""
        try:
            from ..plugins.manager import PluginManager

            self.plugin_manager = PluginManager(console=self.console)
            self.plugin_manager.load_builtin_plugins()

            if self.verbose:
                plugin_count = len(self.plugin_manager.plugins)
                self.console.print(f"[dim]Loaded {plugin_count} plugins[/dim]")

        except ImportError as e:
            if self.verbose:
                self.console.print(f"[yellow]Plugin system not available: {e}[/yellow]")
            self.plugin_manager = None

    def _initialize_state_management(self) -> None:
        """Initialize state management system."""
        try:
            from ..state.manager import StateManager

            if self.config and self.config.storage:
                state_file = self.config.storage.state_file
                lock_file = self.config.storage.lock_file
            else:
                state_file = ".agent/state.yaml"
                lock_file = ".agent/weave.lock"

            self.state_manager = StateManager(
                state_file=state_file, lock_file=lock_file
            )

        except ImportError:
            if self.verbose:
                self.console.print(
                    "[yellow]State management not available[/yellow]"
                )
            self.state_manager = None

    def _initialize_storage(self) -> None:
        """Initialize storage system."""
        try:
            from ..state.storage import Storage

            if self.config and self.config.storage:
                base_path = self.config.storage.base_path
                format = self.config.storage.format
            else:
                base_path = ".agent/storage"
                format = "json"

            self.storage = Storage(base_path=base_path, format=format)

        except ImportError:
            if self.verbose:
                self.console.print("[yellow]Storage system not available[/yellow]")
            self.storage = None

    async def execute_flow(
        self, graph: DependencyGraph, weave_name: str, dry_run: bool = False
    ) -> ExecutionSummary:
        """Execute a complete weave flow.

        Args:
            graph: Dependency graph to execute
            weave_name: Name of the weave
            dry_run: If True, validate but don't execute

        Returns:
            ExecutionSummary with results
        """
        start_time = time.time()

        # Update session with weave name if present
        if self.session:
            self.session.weave_name = weave_name

        # Get execution order
        execution_order = graph.get_execution_order()

        self.console.print(f"\n🧵 [bold cyan]Executing Weave:[/bold cyan] {weave_name}")
        self.console.print(f"[dim]Run ID: {self.run_id}[/dim]")
        self.console.print(
            f"[dim]Order: {' → '.join(execution_order)}[/dim]\n"
        )

        # Initialize state tracking
        if self.state_manager and not dry_run:
            await self._create_execution_state(weave_name, execution_order)

        successful = 0
        failed = 0

        # Execute agents in order
        for agent_name in execution_order:
            agent = graph.config.agents[agent_name]

            # Update session with current agent name
            if self.session:
                self.session.agent_name = agent_name

            try:
                # Execute agent
                output = await self._execute_agent_with_retry(
                    agent, agent_name, dry_run
                )

                # Store output
                self.outputs[output.output_key] = output

                if output.status == "success":
                    successful += 1
                    self.console.print(
                        f"  ✓ [green]{agent_name}[/green] → {output.output_key}"
                    )
                else:
                    failed += 1
                    self.console.print(
                        f"  ✗ [red]{agent_name}[/red] → Failed"
                    )

                # Update state
                if self.state_manager and not dry_run:
                    await self._update_agent_state(agent_name, output)

                # Save output to storage
                if self.storage and not dry_run and agent.storage:
                    if agent.storage.save_outputs:
                        self.storage.save_agent_output(
                            agent_name, output.data, self.run_id
                        )

            except Exception as e:
                failed += 1
                self.console.print(f"  ✗ [red]{agent_name}[/red] → Error: {e}")

                # Store error output
                self.outputs[agent.outputs or agent_name] = AgentOutput(
                    agent_name=agent_name,
                    output_key=agent.outputs or agent_name,
                    data={"error": str(e)},
                    execution_time=0,
                    status="failed",
                    tokens_used=0,
                )

        total_time = time.time() - start_time

        # Finalize state
        if self.state_manager and not dry_run:
            await self._finalize_execution_state(successful, failed, total_time)

        # Save session if enabled
        if self.session and self.session_id and not dry_run:
            from ..core.sessions import get_session_manager
            session_manager = get_session_manager()
            session_manager.save_session(self.session)
            if self.verbose:
                self.console.print(f"[dim]Session saved: {self.session_id}[/dim]")

        self.console.print(
            f"\n[bold]Summary:[/bold] {successful} succeeded, {failed} failed"
        )
        self.console.print(f"[dim]Total time: {total_time:.2f}s[/dim]\n")

        return ExecutionSummary(
            weave_name=weave_name,
            total_agents=len(execution_order),
            successful=successful,
            failed=failed,
            total_time=total_time,
            outputs=self.outputs,
        )

    async def _execute_agent_with_retry(
        self, agent: Agent, agent_name: str, dry_run: bool
    ) -> AgentOutput:
        """Execute agent with retry logic."""
        max_retries = 0
        if self.config and self.config.runtime:
            max_retries = self.config.runtime.max_retries

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await self._execute_agent(agent, agent_name, dry_run)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    if self.verbose:
                        self.console.print(
                            f"[yellow]Retry {attempt + 1}/{max_retries} for {agent_name}[/yellow]"
                        )
                    await asyncio.sleep(1 * (2 ** attempt))  # Exponential backoff

        # All retries failed
        raise last_error

    async def _execute_agent(
        self, agent: Agent, agent_name: str, dry_run: bool
    ) -> AgentOutput:
        """Execute a single agent."""
        start_time = time.time()

        # Call before_agent hooks
        await self._call_before_hooks(agent)

        if dry_run:
            # Dry run: just validate
            await asyncio.sleep(0.1)  # Simulate work
            output = AgentOutput(
                agent_name=agent_name,
                output_key=agent.outputs or agent_name,
                data={"status": "dry-run", "note": "Would execute in real mode"},
                execution_time=0.1,
                status="success",
                tokens_used=0,
            )

            # Call after_agent hooks
            await self._call_after_hooks(agent, output)

            return output

        # Setup memory manager for this agent if configured
        memory_manager = None
        if agent.memory:
            if agent_name not in self.memory_managers:
                memory_manager = MemoryManager(
                    agent_name=agent_name,
                    strategy=agent.memory.type,
                    max_messages=agent.memory.max_messages,
                    context_window=agent.memory.context_window,
                    summarize_after=agent.memory.summarize_after,
                    persist=agent.memory.persist,
                )
                self.memory_managers[agent_name] = memory_manager
            else:
                memory_manager = self.memory_managers[agent_name]

            # Set memory manager on LLM executor
            self.llm_executor.memory_manager = memory_manager

        # Build execution context
        context = {}
        if agent.inputs and agent.inputs in self.outputs:
            context[agent.inputs] = self.outputs[agent.inputs].data

        # Get tools for this agent
        tools = None
        if agent.tools and self.tool_executor:
            tools = await self._prepare_tools(agent.tools)

        # Execute with real LLM
        try:
            llm_response = await self.llm_executor.execute_agent(
                agent, context, tools
            )

            # Handle tool calls if present
            if llm_response.tool_calls:
                final_response = await self._handle_tool_calls(
                    agent, llm_response, context
                )
            else:
                final_response = llm_response

            # Execute plugins if agent has tools
            if agent.tools and self.plugin_manager:
                final_response = await self._execute_plugins(
                    agent, final_response, context
                )

            execution_time = time.time() - start_time

            output = AgentOutput(
                agent_name=agent_name,
                output_key=agent.outputs or agent_name,
                data={
                    "content": final_response.content,
                    "model": final_response.model,
                    "finish_reason": final_response.finish_reason,
                },
                execution_time=execution_time,
                status="success",
                tokens_used=final_response.tokens_used,
            )

            # Call after_agent hooks
            await self._call_after_hooks(agent, output)

            return output

        except Exception as e:
            execution_time = time.time() - start_time
            raise

    async def _prepare_tools(self, tool_names: List[str]) -> List[Dict[str, Any]]:
        """Prepare tool definitions for LLM in OpenAI format."""
        tools = []

        for tool_name in tool_names:
            tool_def = self.tool_executor.get_tool(tool_name)
            if tool_def:
                # Convert to OpenAI tool format
                tool_schema = tool_def.definition.to_json_schema()
                tools.append({
                    "type": "function",
                    "function": tool_schema
                })

        return tools if tools else None

    async def _handle_tool_calls(
        self, agent: Agent, llm_response, context: Dict[str, Any]
    ) -> Any:
        """Handle tool calls from LLM response using unified ToolExecutor."""
        import json

        if not self.tool_executor:
            if self.verbose:
                self.console.print("[yellow]Tool executor not available[/yellow]")
            return llm_response

        # Execute each tool call
        tool_results = []

        for tool_call in llm_response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})

            # Parse arguments if string
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except:
                    pass

            if self.verbose:
                self.console.print(
                    f"[dim]  → Calling tool: {tool_name}[/dim]"
                )

            # Execute tool using unified executor
            try:
                result = await self.tool_executor.execute_async(tool_name, tool_args)

                if "error" in result:
                    if self.verbose:
                        self.console.print(
                            f"[yellow]  ✗ Tool error: {result['error']}[/yellow]"
                        )
                    tool_results.append({
                        "tool": tool_name,
                        "error": result["error"],
                        "success": False
                    })
                else:
                    if self.verbose:
                        result_preview = str(result)[:80]
                        if len(str(result)) > 80:
                            result_preview += "..."
                        self.console.print(
                            f"[dim]  ✓ Result: {result_preview}[/dim]"
                        )
                    tool_results.append({
                        "tool": tool_name,
                        "result": result,
                        "success": True
                    })

            except Exception as e:
                if self.verbose:
                    self.console.print(
                        f"[red]  ✗ Tool exception: {e}[/red]"
                    )
                tool_results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "success": False
                })

        # For now, just return the LLM response
        # In a full implementation, we'd send tool results back to LLM
        return llm_response

    async def _execute_plugins(
        self, agent: Agent, llm_response, context: Dict[str, Any]
    ) -> Any:
        """Execute plugins for agent tools."""
        # For now, plugins don't modify the response
        # In future, plugins could post-process LLM outputs
        return llm_response

    async def _call_before_hooks(self, agent: Agent) -> None:
        """
        Call before_agent hooks with error handling.

        Hooks are called in registration order. If a hook raises an exception,
        it is logged but does not stop execution.
        """
        for hook in self.hooks:
            try:
                await hook.before_agent(agent)
            except Exception as e:
                # Log hook errors but don't fail execution
                if self.verbose:
                    self.console.print(
                        f"[yellow]Hook {type(hook).__name__}.before_agent() "
                        f"failed: {e}[/yellow]"
                    )

    async def _call_after_hooks(self, agent: Agent, output: AgentOutput) -> None:
        """
        Call after_agent hooks with error handling.

        Hooks are called in registration order. If a hook raises an exception,
        it is logged but does not stop execution.
        """
        for hook in self.hooks:
            try:
                await hook.after_agent(agent, output)
            except Exception as e:
                # Log hook errors but don't fail execution
                if self.verbose:
                    self.console.print(
                        f"[yellow]Hook {type(hook).__name__}.after_agent() "
                        f"failed: {e}[/yellow]"
                    )

    async def _create_execution_state(
        self, weave_name: str, agents: List[str]
    ) -> None:
        """Create initial execution state."""
        if self.state_manager:
            self.state_manager.create_execution_state(
                run_id=self.run_id, weave_name=weave_name, agent_names=agents
            )

    async def _update_agent_state(
        self, agent_name: str, output: AgentOutput
    ) -> None:
        """Update agent execution state."""
        if self.state_manager:
            self.state_manager.update_agent_status(
                run_id=self.run_id,
                agent_name=agent_name,
                status=output.status,
                duration=output.execution_time,
                tokens=output.tokens_used,
            )

    async def _finalize_execution_state(
        self, successful: int, failed: int, total_time: float
    ) -> None:
        """Finalize execution state."""
        if self.state_manager:
            status = "completed" if failed == 0 else "failed"
            self.state_manager.finalize_execution(self.run_id, status, total_time)
