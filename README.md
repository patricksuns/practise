# Multi-Agent Runner Framework

A minimal viable product (MVP) multi-agent orchestration framework for Python quantitative research and engineering automation, with GitHub API integration for automatic pull request creation.

## Overview

This framework implements a multi-agent system where specialized agents collaborate to complete complex workflows:

- **Planner**: Creates execution plans and task breakdowns
- **Quant Researcher**: Analyzes data and develops quantitative strategies
- **Data Engineer**: Designs and implements data pipelines
- **Engineer**: Implements code changes and features
- **Critic**: Reviews code and provides feedback

Each agent follows a structured output protocol with both human-readable summaries and machine-parsable YAML data, enabling seamless orchestration and state management.

## Features

✅ **Multi-Agent Orchestration**: Automatic workflow coordination with state management  
✅ **Structured Output Protocol**: YAML-based agent communication  
✅ **Mock Mode**: Rule-based operation without LLM for testing and validation  
✅ **GitHub Integration**: Automatic PR creation using Personal Access Token  
✅ **Git Operations**: Automated branch creation, commits, and push  
✅ **State Persistence**: Workflow state saved as YAML/JSON  
✅ **Human-Readable Reports**: Markdown reports for workflow execution  

## Directory Structure

```
practise/
├── orchestrator/          # Workflow orchestration
│   ├── run.py            # CLI main entry point
│   ├── state.py          # State management (YAML/JSON)
│   ├── github_api.py     # GitHub REST API wrapper
│   ├── git_ops.py        # Git operations
│   └── __init__.py
├── agents/               # Agent implementations
│   ├── base.py          # Base agent class and protocol
│   ├── planner.py
│   ├── quant_researcher.py
│   ├── data_engineer.py
│   ├── engineer.py
│   ├── critic.py
│   └── __init__.py
├── prompts/             # Agent prompt templates
│   ├── planner.md
│   ├── quant_researcher.md
│   ├── data_engineer.md
│   ├── engineer.md
│   └── critic.md
├── reports/             # Generated reports (gitignored)
│   └── .gitignore
└── README.md
```

## Installation

### Prerequisites

- Python 3.7+
- Git
- GitHub Personal Access Token (for PR creation)

### Dependencies

```bash
pip install pyyaml requests
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

For PR creation functionality, set the following environment variables:

```bash
# Required for creating pull requests
export GITHUB_TOKEN="your_github_personal_access_token"

# Optional: auto-detected from git remote if not set
export GITHUB_REPOSITORY="owner/repo"
```

### Creating a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Generate and copy the token
5. Set it as an environment variable: `export GITHUB_TOKEN="your_token"`

## Usage

### Basic Workflow Execution (Mock Mode)

Run an engineering workflow:
```bash
python orchestrator/run.py --workflow engineering --task "Refactor error handling"
```

Run a quantitative research workflow:
```bash
python orchestrator/run.py --workflow quant --task "Develop momentum trading strategy"
```

### With Pull Request Creation

```bash
# Set GitHub token first
export GITHUB_TOKEN="ghp_your_token_here"

# Run workflow and create PR
python orchestrator/run.py \
  --workflow engineering \
  --task "Add comprehensive logging" \
  --create-pr
```

### Command-Line Options

```
--workflow {engineering,quant}  Workflow type to execute (required)
--task TASK                     Task description (required)
--mock-mode                     Use mock mode (default, no LLM needed)
--llm-mode                      Use LLM mode (requires integration)
--create-pr                     Create pull request after completion
--base-branch BRANCH            Base branch for PR (default: main)
```

### Example Workflows

#### Engineering Workflow
```bash
python orchestrator/run.py \
  --workflow engineering \
  --task "Implement user authentication system" \
  --create-pr
```

Typical flow: `planner → engineer → critic`

#### Quantitative Research Workflow
```bash
python orchestrator/run.py \
  --workflow quant \
  --task "Backtest mean-reversion strategy" \
  --create-pr
```

Typical flow: `planner → quant_researcher → data_engineer → engineer → critic`

## Output Protocol

Each agent produces structured output with two components:

### 1. Human-Readable Summary
Plain text description of the agent's work and findings.

### 2. Machine-Parsable YAML
Structured data including:

```yaml
agent_name: "planner"
findings:
  - "Key observation 1"
  - "Key observation 2"
decisions:
  - "Decision 1"
  - "Decision 2"
tasks:
  - id: 1
    description: "Task description"
    assigned_to: "agent_name"
risks:
  - "Potential risk 1"
metrics:
  key1: value1
  key2: value2
next_agent: "next_agent_name"  # or null to end workflow
```

## Mock Mode vs LLM Mode

### Mock Mode (Current Implementation)
- **Default operation mode**
- Generates rule-based outputs based on workflow type
- No external LLM API calls required
- Perfect for testing, CI/CD, and validation
- Demonstrates complete workflow orchestration

### LLM Mode (Future Extension)
To integrate with real LLM services:

1. Implement LLM client in `orchestrator/llm_client.py`
2. Update agent `process()` methods to use LLM when `mock_mode=False`
3. Add LLM configuration (API keys, model names, etc.)
4. Example integration:

```python
# In agents/planner.py
def process(self, request, mock_mode=True):
    if mock_mode:
        return self._mock_process(request)
    else:
        # Load prompt template
        prompt = self.load_prompt_template('prompts/planner.md')
        
        # Call LLM
        from orchestrator.llm_client import LLMClient
        llm = LLMClient()
        response = llm.complete(prompt, request)
        
        # Parse and return
        return self._parse_llm_response(response)
```

## Workflow State Management

States are automatically saved to `reports/` directory:

- `{run_id}_state.yaml`: Complete workflow state
- `{run_id}_report.md`: Human-readable execution report

Example state structure:
```yaml
run_id: run_engineering_20260103_091234
workflow_type: engineering
task_description: "Add logging functionality"
created_at: "2026-01-03T09:12:34"
current_stage: "workflow_complete"
current_agent: "critic"
agent_outputs:
  - agent_name: "planner"
    timestamp: "2026-01-03T09:12:35"
    summary: "..."
    structured_data: {...}
  - agent_name: "engineer"
    timestamp: "2026-01-03T09:12:36"
    summary: "..."
    structured_data: {...}
```

## GitHub API Integration

The framework uses GitHub REST API v3 with Personal Access Token authentication:

### Supported Operations
- Create pull requests
- Get pull request details
- Update pull requests
- List pull requests
- Get repository information

### Error Handling
The framework handles common GitHub API errors:
- Invalid token
- Rate limiting
- Branch conflicts
- Permission issues

## Git Operations

Automated git operations include:
- Branch creation: `agent/{workflow_type}/{run_id}`
- File staging and commits
- Push to remote with upstream tracking
- Status checking

## Testing the Framework

### End-to-End Test (Without PR Creation)

```bash
# Run a complete workflow in mock mode
python orchestrator/run.py \
  --workflow engineering \
  --task "Test the multi-agent framework"

# Check the generated reports
ls -la reports/
cat reports/run_engineering_*_report.md
```

### End-to-End Test (With PR Creation)

```bash
# Ensure you're on a test branch or feature branch, not main
git checkout -b test-multi-agent

# Set GitHub token
export GITHUB_TOKEN="your_token"

# Run workflow with PR creation
python orchestrator/run.py \
  --workflow quant \
  --task "Test PR creation" \
  --create-pr \
  --base-branch main

# Check the created PR on GitHub
```

## Architecture Decisions

### Why Mock Mode First?
- **Reproducibility**: Anyone can run and test without LLM API keys
- **CI/CD Ready**: Can be integrated into automated pipelines
- **Development**: Easier to develop and debug orchestration logic
- **Cost**: No API costs during development and testing

### Why YAML for State?
- **Human-readable**: Easy to inspect and debug
- **Git-friendly**: Clear diffs for version control
- **Flexible**: Can be converted to JSON if needed

### Why Structured Output Protocol?
- **Reliable Parsing**: Machine-parsable format eliminates ambiguity
- **Type Safety**: Clear schema for agent communication
- **Extensibility**: Easy to add new fields without breaking existing code

## Troubleshooting

### "GitHub token not provided"
Solution: Set the `GITHUB_TOKEN` environment variable:
```bash
export GITHUB_TOKEN="your_token_here"
```

### "Repository owner and name not provided"
Solution: Set the `GITHUB_REPOSITORY` environment variable:
```bash
export GITHUB_REPOSITORY="owner/repo"
```

Or the git remote will be auto-detected.

### "Failed to create PR: 422"
This usually means:
- Branch already has an open PR
- Branch name already exists
- No changes between base and head branches

### Import Errors
Make sure you're running from the repository root:
```bash
cd /path/to/practise
python orchestrator/run.py --workflow engineering --task "test"
```

## Future Enhancements

Potential extensions for the framework:

1. **LLM Integration**
   - OpenAI GPT-4
   - Anthropic Claude
   - Local models (Ollama, LLaMA)

2. **Additional Agents**
   - Tester: Generate and run tests
   - Documenter: Update documentation
   - Security Auditor: Check for vulnerabilities

3. **Enhanced State Management**
   - State versioning
   - Workflow rollback
   - Checkpoint/resume functionality

4. **Advanced Features**
   - Parallel agent execution
   - Agent delegation and sub-tasks
   - Human-in-the-loop approvals
   - Slack/Discord notifications

5. **Web UI**
   - Dashboard for workflow monitoring
   - Interactive agent configuration
   - Real-time execution logs

## Contributing

This is a practice repository. Feel free to fork and experiment!

## License

MIT License - See repository for details.

---

**Note**: This is an MVP implementation focused on demonstrating the multi-agent orchestration concept with GitHub integration. Production use would require additional error handling, monitoring, and LLM integration.