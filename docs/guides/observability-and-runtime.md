# Observability and Runtime Configuration

Complete guide to observability, monitoring, and runtime configuration in Weave.

## Table of Contents

- [Overview](#overview)
- [Observability Configuration](#observability-configuration)
  - [Logging](#logging)
  - [Metrics](#metrics)
  - [Tracing](#tracing)
  - [Export Options](#export-options)
- [Runtime Configuration](#runtime-configuration)
  - [Execution Mode](#execution-mode)
  - [Retry Policies](#retry-policies)
  - [Timeouts](#timeouts)
  - [Rate Limiting](#rate-limiting)
  - [Resource Limits](#resource-limits)
  - [Error Handling](#error-handling)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

## Overview

Weave provides comprehensive observability and runtime configuration to help you:

- **Monitor** agent execution in real-time
- **Debug** issues with detailed logging and tracing
- **Measure** performance with metrics and analytics
- **Control** execution behavior with flexible runtime settings
- **Optimize** resource usage and reliability

All configuration is done through YAML - no code changes required.

## Observability Configuration

Configure logging, metrics, and tracing for complete visibility into your workflows.

```yaml
observability:
  # Logging
  enabled: true
  log_level: "INFO"
  log_format: "json"

  # Metrics
  collect_metrics: true
  track_token_usage: true

  # Tracing
  enable_tracing: false
```

### Logging

Control what gets logged and how.

#### Configuration Options

```yaml
observability:
  # Basic logging
  enabled: true
  log_level: "INFO"              # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_format: "json"             # json, text, structured
  log_file: ".weave/logs/weave.log"
  log_to_console: true

  # What to log
  log_agent_inputs: true         # Log inputs to agents
  log_agent_outputs: true        # Log agent outputs
  log_tool_calls: true           # Log tool invocations
```

#### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause termination

#### Log Formats

**JSON** (Structured):
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "agent": "researcher",
  "event": "agent_started",
  "metadata": {"model": "gpt-4"}
}
```

**Text** (Human-readable):
```
2024-01-15 10:30:45 [INFO] agent.researcher: Agent started (model=gpt-4)
```

**Structured** (Key-value):
```
timestamp=2024-01-15T10:30:45Z level=INFO agent=researcher event=agent_started model=gpt-4
```

#### Example

```yaml
observability:
  enabled: true
  log_level: "DEBUG"
  log_format: "json"
  log_file: ".weave/logs/production.log"
  log_to_console: true

  # Verbose logging for debugging
  log_agent_inputs: true
  log_agent_outputs: true
  log_tool_calls: true
```

### Metrics

Track performance and usage metrics.

#### Configuration Options

```yaml
observability:
  # Metrics collection
  collect_metrics: true
  metrics_format: "prometheus"    # prometheus, statsd, datadog
  metrics_endpoint: "http://localhost:9090"

  # What to track
  track_token_usage: true         # LLM token consumption
  track_latency: true             # Execution time
  track_success_rate: true        # Success/failure rates
```

#### Available Metrics

**Execution Metrics**:
- Agent execution time (latency)
- Total workflow execution time
- Queue time (waiting for execution)

**Resource Metrics**:
- Token usage per agent
- Token usage per model
- Memory consumption
- CPU usage

**Quality Metrics**:
- Success rate per agent
- Failure rate per agent
- Retry count
- Error types and frequencies

#### Metrics Formats

**Prometheus**:
```
# HELP weave_agent_duration_seconds Time taken to execute agent
# TYPE weave_agent_duration_seconds histogram
weave_agent_duration_seconds{agent="researcher",model="gpt-4"} 2.5
```

**StatsD**:
```
weave.agent.duration:2.5|ms|#agent:researcher,model:gpt-4
weave.agent.tokens:1250|c|#agent:researcher,model:gpt-4
```

**Datadog**:
```json
{
  "series": [{
    "metric": "weave.agent.duration",
    "points": [[1642242645, 2.5]],
    "tags": ["agent:researcher", "model:gpt-4"]
  }]
}
```

### Tracing

Enable distributed tracing for complex workflows.

#### Configuration Options

```yaml
observability:
  # Distributed tracing
  enable_tracing: true
  tracing_backend: "opentelemetry"  # opentelemetry, jaeger, zipkin
  tracing_endpoint: "http://localhost:4318"
  trace_sampling_rate: 1.0          # 0.0 to 1.0 (100%)
```

#### Tracing Backends

**OpenTelemetry** (Recommended):
```yaml
observability:
  enable_tracing: true
  tracing_backend: "opentelemetry"
  tracing_endpoint: "http://localhost:4318/v1/traces"
  trace_sampling_rate: 1.0
```

**Jaeger**:
```yaml
observability:
  enable_tracing: true
  tracing_backend: "jaeger"
  tracing_endpoint: "http://localhost:14268/api/traces"
  trace_sampling_rate: 0.1  # Sample 10% of traces
```

**Zipkin**:
```yaml
observability:
  enable_tracing: true
  tracing_backend: "zipkin"
  tracing_endpoint: "http://localhost:9411/api/v2/spans"
```

#### Trace Information

Each trace includes:
- Span for each agent execution
- Span for each tool call
- Parent-child relationships
- Timestamps and durations
- Metadata (model, inputs, outputs)
- Error information

### Export Options

Export logs, metrics, and traces to files or external systems.

```yaml
observability:
  # Export configuration
  export_traces: true
  export_metrics: true
  export_logs: true
  export_dir: ".weave/exports"
```

Exported data is saved in standard formats:
- **Traces**: OpenTelemetry JSON or Jaeger JSON
- **Metrics**: Prometheus text format or JSON
- **Logs**: JSONL (JSON Lines) or plain text

---

## Runtime Configuration

Control how your workflows execute.

```yaml
runtime:
  # Execution
  mode: "sequential"
  max_concurrent_agents: 1

  # Retry policy
  max_retries: 3
  retry_backoff: "exponential"

  # Timeouts
  default_timeout: 300.0
  weave_timeout: 3600.0
```

### Execution Mode

Control how agents are executed.

#### Sequential Mode

Agents execute one at a time in dependency order.

```yaml
runtime:
  mode: "sequential"
  max_concurrent_agents: 1
```

**Use cases**:
- Simple workflows
- Limited resources
- Debugging

#### Parallel Mode

Independent agents execute concurrently.

```yaml
runtime:
  mode: "parallel"
  max_concurrent_agents: 5
```

**Use cases**:
- Multiple independent agents
- Faster execution
- Resource-intensive workflows

#### Async Mode

Agents execute asynchronously with event-driven coordination.

```yaml
runtime:
  mode: "async"
  max_concurrent_agents: 10
```

**Use cases**:
- High-throughput workflows
- I/O-bound operations
- Complex dependency graphs

### Retry Policies

Configure how failures are handled with automatic retries.

#### Basic Retry Configuration

```yaml
runtime:
  max_retries: 3                  # Retry up to 3 times
  retry_delay: 1.0                # Initial delay: 1 second
  retry_backoff: "exponential"    # exponential, linear, constant
  retry_backoff_multiplier: 2.0   # Double delay each retry

  # Retry on specific errors
  retry_on_errors:
    - "timeout"
    - "api_error"
    - "rate_limit"
```

#### Backoff Strategies

**Exponential Backoff** (Recommended):
```yaml
runtime:
  retry_backoff: "exponential"
  retry_delay: 1.0
  retry_backoff_multiplier: 2.0
```
Delays: 1s, 2s, 4s, 8s, ...

**Linear Backoff**:
```yaml
runtime:
  retry_backoff: "linear"
  retry_delay: 1.0
  retry_backoff_multiplier: 1.0
```
Delays: 1s, 2s, 3s, 4s, ...

**Constant Backoff**:
```yaml
runtime:
  retry_backoff: "constant"
  retry_delay: 2.0
```
Delays: 2s, 2s, 2s, 2s, ...

#### Example: Robust Retry Policy

```yaml
runtime:
  max_retries: 5
  retry_delay: 2.0
  retry_backoff: "exponential"
  retry_backoff_multiplier: 2.0
  retry_on_errors:
    - "timeout"
    - "api_error"
    - "rate_limit"
    - "connection_error"
    - "server_error"
```

### Timeouts

Prevent agents from running indefinitely.

```yaml
runtime:
  default_timeout: 300.0    # 5 minutes per agent
  weave_timeout: 3600.0     # 1 hour total
  tool_timeout: 60.0        # 1 minute per tool call
```

#### Timeout Behavior

- **default_timeout**: Maximum time for single agent execution
- **weave_timeout**: Maximum time for entire workflow
- **tool_timeout**: Maximum time for tool calls

If timeout is exceeded:
1. Execution is terminated
2. Error is logged
3. Retry policy is applied (if configured)
4. Workflow continues or stops based on error handling settings

### Rate Limiting

Control API request rates to avoid throttling.

```yaml
runtime:
  enable_rate_limiting: true
  requests_per_minute: 60
  tokens_per_minute: 100000
```

**Use cases**:
- API rate limit compliance
- Cost control
- Resource management

### Resource Limits

Limit resource consumption per agent.

```yaml
runtime:
  max_memory_mb: 2048       # 2GB max memory
  max_cpu_percent: 80.0     # 80% max CPU
```

**Note**: Resource limits require system support and may not be available on all platforms.

### Error Handling

Configure behavior when errors occur.

```yaml
runtime:
  stop_on_error: true                  # Stop on first error
  continue_on_agent_failure: false     # Continue if agent fails
  save_partial_results: true           # Save successful agent outputs
```

#### Error Handling Strategies

**Fail Fast** (Default):
```yaml
runtime:
  stop_on_error: true
  continue_on_agent_failure: false
  save_partial_results: true
```
Stop immediately on any error, save partial results.

**Continue on Failure**:
```yaml
runtime:
  stop_on_error: false
  continue_on_agent_failure: true
  save_partial_results: true
```
Continue executing independent agents even if some fail.

**Best Effort**:
```yaml
runtime:
  stop_on_error: false
  continue_on_agent_failure: true
  save_partial_results: true
  max_retries: 3
```
Try to complete as much as possible with retries.

---

## Complete Examples

### Production Workflow

High-reliability configuration for production environments.

```yaml
version: "1.0"

observability:
  enabled: true
  log_level: "INFO"
  log_format: "json"
  log_file: "/var/log/weave/production.log"
  log_to_console: false

  collect_metrics: true
  metrics_format: "prometheus"
  metrics_endpoint: "http://prometheus:9090"
  track_token_usage: true
  track_latency: true
  track_success_rate: true

  enable_tracing: true
  tracing_backend: "opentelemetry"
  tracing_endpoint: "http://jaeger:4318/v1/traces"
  trace_sampling_rate: 0.1

  export_logs: true
  export_metrics: true
  export_traces: true
  export_dir: "/var/log/weave/exports"

runtime:
  mode: "parallel"
  max_concurrent_agents: 5
  enable_caching: true

  max_retries: 3
  retry_delay: 2.0
  retry_backoff: "exponential"
  retry_backoff_multiplier: 2.0
  retry_on_errors: ["timeout", "api_error", "rate_limit"]

  default_timeout: 300.0
  weave_timeout: 1800.0
  tool_timeout: 60.0

  enable_rate_limiting: true
  requests_per_minute: 100
  tokens_per_minute: 150000

  stop_on_error: false
  continue_on_agent_failure: true
  save_partial_results: true

agents:
  # ... agent definitions
```

### Development/Debug Configuration

Verbose configuration for development and debugging.

```yaml
version: "1.0"

observability:
  enabled: true
  log_level: "DEBUG"
  log_format: "text"
  log_file: ".weave/logs/debug.log"
  log_to_console: true

  log_agent_inputs: true
  log_agent_outputs: true
  log_tool_calls: true

  collect_metrics: true
  track_token_usage: true
  track_latency: true

  enable_tracing: true
  trace_sampling_rate: 1.0

  export_logs: true
  export_dir: ".weave/debug"

runtime:
  mode: "sequential"
  max_concurrent_agents: 1

  max_retries: 0
  default_timeout: 600.0

  stop_on_error: true
  save_partial_results: true
  verbose: true
  debug: true

agents:
  # ... agent definitions
```

### Performance-Optimized Configuration

Maximize throughput with minimal overhead.

```yaml
version: "1.0"

observability:
  enabled: true
  log_level: "WARNING"           # Only warnings and errors
  log_format: "json"
  log_to_console: false

  log_agent_inputs: false        # Reduce logging overhead
  log_agent_outputs: false
  log_tool_calls: false

  collect_metrics: true
  metrics_format: "statsd"       # Lightweight metrics
  track_token_usage: true

  enable_tracing: false          # Disable tracing overhead

runtime:
  mode: "async"
  max_concurrent_agents: 20
  enable_caching: true

  max_retries: 1                 # Quick retries only
  retry_delay: 0.5
  retry_backoff: "constant"

  default_timeout: 120.0
  weave_timeout: 600.0

  enable_rate_limiting: true
  requests_per_minute: 200

  continue_on_agent_failure: true
  save_partial_results: true

agents:
  # ... agent definitions
```

---

## Best Practices

### Observability

1. **Use JSON logging in production**:
   - Easier to parse and analyze
   - Better for log aggregation systems
   - Structured data for querying

2. **Set appropriate log levels**:
   - Development: DEBUG or INFO
   - Production: INFO or WARNING
   - Reduce noise, focus on important events

3. **Enable metrics collection**:
   - Track performance over time
   - Identify bottlenecks
   - Monitor costs (token usage)

4. **Use sampling for tracing**:
   - 100% sampling in development
   - 1-10% sampling in production
   - Reduces overhead while maintaining visibility

5. **Export to external systems**:
   - Use Prometheus for metrics
   - Use Jaeger or Zipkin for traces
   - Use ELK stack for logs

### Runtime Configuration

1. **Choose the right execution mode**:
   - Sequential for simple workflows
   - Parallel for independent agents
   - Async for high-throughput

2. **Configure retries appropriately**:
   - Use exponential backoff
   - Retry only transient errors
   - Set max retries (3-5 recommended)

3. **Set reasonable timeouts**:
   - Consider model response times
   - Account for network latency
   - Allow buffer for retries

4. **Enable rate limiting**:
   - Comply with API limits
   - Avoid throttling
   - Control costs

5. **Handle errors gracefully**:
   - Save partial results
   - Log detailed error information
   - Continue on non-critical failures

### Security and Privacy

1. **Protect sensitive data in logs**:
   - Don't log API keys or credentials
   - Redact PII from logs
   - Use secure log storage

2. **Secure metrics endpoints**:
   - Use authentication
   - Encrypt traffic (HTTPS)
   - Restrict access

3. **Control trace data**:
   - Don't include sensitive inputs/outputs
   - Use sampling in production
   - Secure trace storage

### Performance

1. **Minimize logging overhead**:
   - Disable verbose logging in production
   - Use async logging
   - Rotate log files

2. **Optimize metrics collection**:
   - Use efficient formats (StatsD)
   - Aggregate metrics locally
   - Send in batches

3. **Balance observability and performance**:
   - Disable tracing for high-throughput workflows
   - Use sampling appropriately
   - Monitor overhead

## Summary

- ✅ Configure comprehensive observability (logs, metrics, traces)
- ✅ Control execution with runtime configuration
- ✅ Implement retry policies for reliability
- ✅ Set timeouts to prevent hangs
- ✅ Enable rate limiting for API compliance
- ✅ Handle errors gracefully
- ✅ Use appropriate settings for each environment
- ✅ Balance observability and performance

## Next Steps

- [Configuration Reference](../reference/configuration.md)
- [Testing Guide](testing.md)
- [Tool Calling Guide](tool-calling.md)
- [Examples](../../examples/)
