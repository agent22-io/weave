# Example Interaction: Creating a Research Summarizer Agent

This document shows a complete walkthrough of creating an agent using the Agent Creator MCP server.

## Scenario

A user wants to create an agent that reads research papers and generates concise summaries highlighting key findings, methodology, and conclusions.

## Complete Interaction

### Starting the Session

**User:**
> I need to create an agent that can summarize research papers. Can you help me set this up?

**Agent Designer:**
> Of course! I'll guide you through creating a Weave agent for summarizing research papers. Let me start an interactive session.

*[Tool Call: start_agent_creation(session_id="research-summary-001")]*

```json
{
  "status": "started",
  "message": "Agent creation session started! I'll guide you through creating a Weave agent.",
  "next_question": {
    "step": 0,
    "question": "What is the name of your agent?",
    "field": "agent_name",
    "hint": "Choose a descriptive name (e.g., 'researcher', 'writer', 'analyzer')",
    "example": "content_researcher"
  }
}
```

**Agent Designer:**
> Great! Let's get started. First question:
>
> **What is the name of your agent?**
>
> Choose a descriptive name like 'researcher', 'writer', or 'analyzer'.
> Example: content_researcher

---

### Question 1: Agent Name

**User:**
> research_summarizer

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="research_summarizer")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: research_summarizer",
  "next_question": {
    "step": 1,
    "question": "What is the purpose of this agent?",
    "field": "description",
    "hint": "Describe what this agent does in 1-2 sentences",
    "example": "Researches topics and gathers relevant information"
  },
  "progress": "1/8 questions answered"
}
```

**Agent Designer:**
> Perfect! (Progress: 1/8)
>
> **What is the purpose of this agent?**
>
> Describe what this agent does in 1-2 sentences.

---

### Question 2: Description

**User:**
> Analyzes research papers and creates concise summaries that highlight key findings, methodology, and conclusions for quick understanding

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="Analyzes research papers and creates concise summaries that highlight key findings, methodology, and conclusions for quick understanding")]*

```json
{
  "status": "continue",
  "message": "Answer recorded",
  "next_question": {
    "step": 2,
    "question": "Which LLM model should this agent use?",
    "field": "model",
    "hint": "Choose from: gpt-4, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet, claude-3-haiku",
    "example": "gpt-4"
  },
  "progress": "2/8 questions answered"
}
```

**Agent Designer:**
> Excellent description! (Progress: 2/8)
>
> **Which LLM model should this agent use?**
>
> Available options:
> - gpt-4 (most capable, slower)
> - gpt-3.5-turbo (fast, cost-effective)
> - claude-3-opus (best reasoning)
> - claude-3-sonnet (balanced performance)
> - claude-3-haiku (fastest, efficient)

---

### Question 3: Model

**User:**
> claude-3-sonnet

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="claude-3-sonnet")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: claude-3-sonnet",
  "next_question": {
    "step": 3,
    "question": "What tools should this agent have access to?",
    "field": "tools",
    "hint": "Comma-separated list. Available: web_search, calculator, text_length, json_validator, string_formatter",
    "example": "web_search, summarizer"
  },
  "progress": "3/8 questions answered"
}
```

**Agent Designer:**
> Good choice! Claude Sonnet offers great balance. (Progress: 3/8)
>
> **What tools should this agent have access to?**
>
> Available tools (comma-separated):
> - web_search - Search for information online
> - calculator - Perform calculations
> - text_length - Count words/characters
> - json_validator - Validate JSON data
> - string_formatter - Format strings

---

### Question 4: Tools

**User:**
> text_length, string_formatter

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="text_length, string_formatter")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: text_length, string_formatter",
  "next_question": {
    "step": 4,
    "question": "What temperature should the model use? (0.0-1.0)",
    "field": "temperature",
    "hint": "Lower = more deterministic, Higher = more creative. Default is 0.7",
    "example": "0.7"
  },
  "progress": "4/8 questions answered"
}
```

**Agent Designer:**
> Great tool selection for summarization! (Progress: 4/8)
>
> **What temperature should the model use? (0.0-1.0)**
>
> - Lower values (0.1-0.3): More focused, deterministic, factual
> - Medium values (0.4-0.7): Balanced creativity and consistency
> - Higher values (0.8-1.0): More creative and varied outputs
>
> For summarization, lower temperatures work well.

---

### Question 5: Temperature

**User:**
> 0.3

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="0.3")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: 0.3",
  "next_question": {
    "step": 5,
    "question": "Maximum tokens for responses?",
    "field": "max_tokens",
    "hint": "Maximum length of generated responses. Default is 1000",
    "example": "1000"
  },
  "progress": "5/8 questions answered"
}
```

**Agent Designer:**
> Perfect for factual summarization! (Progress: 5/8)
>
> **Maximum tokens for responses?**
>
> This controls the maximum length of generated summaries.
> - 500-1000: Short summaries
> - 1000-2000: Medium-length summaries
> - 2000+: Detailed summaries

---

### Question 6: Max Tokens

**User:**
> 1500

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="1500")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: 1500",
  "next_question": {
    "step": 6,
    "question": "Does this agent depend on another agent's output? (optional)",
    "field": "inputs",
    "hint": "Name of another agent this one depends on, or leave empty",
    "example": "researcher (or leave empty)"
  },
  "progress": "6/8 questions answered"
}
```

**Agent Designer:**
> Good length for medium summaries. (Progress: 6/8)
>
> **Does this agent depend on another agent's output? (optional)**
>
> If this agent needs data from another agent, specify its name.
> Otherwise, leave empty for a standalone agent.

---

### Question 7: Inputs (Dependencies)

**User:**
> (leave empty - standalone agent)

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="")]*

```json
{
  "status": "continue",
  "message": "Answer recorded: ",
  "next_question": {
    "step": 7,
    "question": "What should the output be named?",
    "field": "outputs",
    "hint": "Name for this agent's output that other agents can reference",
    "example": "research_summary"
  },
  "progress": "7/8 questions answered"
}
```

**Agent Designer:**
> Got it - standalone agent. (Progress: 7/8)
>
> **What should the output be named?**
>
> This name can be used by other agents to reference this agent's output.
> Example: "research_summary", "analysis_result", "processed_data"

---

### Question 8: Output Name

**User:**
> paper_summary

**Agent Designer:**

*[Tool Call: answer_question(session_id="research-summary-001", answer="paper_summary")]*

```json
{
  "status": "complete",
  "message": "Agent configuration created successfully!",
  "agent_name": "research_summarizer",
  "configuration": "version: \"1.0\"\n\nagents:\n  research_summarizer:\n    # Analyzes research papers and creates concise summaries that highlight key findings, methodology, and conclusions for quick understanding\n    model: \"claude-3-sonnet\"\n    tools: [text_length, string_formatter]\n    outputs: \"paper_summary\"\n    config:\n      temperature: 0.3\n      max_tokens: 1500"
}
```

---

## Generated Configuration

**Agent Designer:**
> 🎉 Perfect! Your agent configuration is complete!
>
> Here's the YAML configuration for your research_summarizer agent:

```yaml
version: "1.0"

agents:
  research_summarizer:
    # Analyzes research papers and creates concise summaries that highlight key findings, methodology, and conclusions for quick understanding
    model: "claude-3-sonnet"
    tools: [text_length, string_formatter]
    outputs: "paper_summary"
    config:
      temperature: 0.3
      max_tokens: 1500
```

> You can save this to a `.weave.yaml` file and run it with:
> ```bash
> weave apply --real
> ```
>
> Would you like me to validate this configuration or make any changes?

---

## Summary

In this interaction, the Agent Creator:

1. ✅ Started a new session
2. ✅ Asked 8 structured questions
3. ✅ Validated each answer
4. ✅ Generated a complete YAML configuration
5. ✅ Provided usage instructions

**Total Questions:** 8
**Time to Create:** ~2-3 minutes
**Configuration Valid:** ✓ Yes
**Ready to Deploy:** ✓ Yes

## Next Steps

The user can now:
- Save the configuration to `.weave.yaml`
- Test with `weave plan`
- Execute with `weave apply --real`
- Add this agent to a larger workflow
- Create more agents and compose them together
