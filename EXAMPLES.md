# Examples - Multi-Agent Runner Framework

This document provides practical examples and use cases for the Multi-Agent Runner Framework.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Engineering Workflow Examples](#engineering-workflow-examples)
- [Quantitative Research Workflow Examples](#quantitative-research-workflow-examples)
- [Understanding the Output](#understanding-the-output)
- [GitHub Integration Examples](#github-integration-examples)
- [Troubleshooting](#troubleshooting)

## Basic Usage

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# For PR creation, set GitHub token
export GITHUB_TOKEN="ghp_your_token_here"
```

### Running Your First Workflow

```bash
# Simple engineering workflow
python orchestrator/run.py \
  --workflow engineering \
  --task "Add input validation to user registration"

# Simple quant workflow  
python orchestrator/run.py \
  --workflow quant \
  --task "Analyze momentum indicators"
```

## Engineering Workflow Examples

### Example 1: Code Refactoring

```bash
python orchestrator/run.py \
  --workflow engineering \
  --task "Refactor database connection pooling for better performance"
```

**What happens:**
1. **Planner** analyzes the task and creates an execution plan
2. **Engineer** implements the refactoring changes
3. **Critic** reviews the code for quality and best practices

**Output files:**
- `reports/run_engineering_TIMESTAMP_state.yaml` - Machine-readable state
- `reports/run_engineering_TIMESTAMP_report.md` - Human-readable report

### Example 2: Bug Fix with PR

```bash
export GITHUB_TOKEN="your_token"

python orchestrator/run.py \
  --workflow engineering \
  --task "Fix memory leak in background task processor" \
  --create-pr \
  --base-branch main
```

**What happens:**
1. Workflow executes: planner → engineer → critic
2. Changes are committed to a new branch: `agent/engineering/run_engineering_TIMESTAMP`
3. Pull request is automatically created with workflow results

### Example 3: Adding New Feature

```bash
python orchestrator/run.py \
  --workflow engineering \
  --task "Implement JWT authentication for API endpoints" \
  --create-pr
```

**Expected PR:**
- Title: `[ENGINEERING] Implement JWT authentication for API endpoints`
- Body: Contains summary of all agent outputs
- Branch: `agent/engineering/run_engineering_TIMESTAMP`

## Quantitative Research Workflow Examples

### Example 1: Strategy Development

```bash
python orchestrator/run.py \
  --workflow quant \
  --task "Develop mean-reversion strategy for equity markets"
```

**What happens:**
1. **Planner** outlines the research workflow
2. **Quant Researcher** analyzes data and proposes strategy
3. **Data Engineer** designs data pipeline architecture
4. **Engineer** implements the strategy code
5. **Critic** reviews the implementation

**Typical output includes:**
- Strategy parameters (lookback periods, thresholds)
- Performance metrics (Sharpe ratio, max drawdown)
- Data pipeline design
- Implementation details

### Example 2: Backtesting Analysis

```bash
python orchestrator/run.py \
  --workflow quant \
  --task "Backtest momentum strategy with different parameter sets"
```

**Quant Researcher output includes:**
```yaml
metrics:
  sharpe_ratio: 1.35
  max_drawdown: 0.12
  win_rate: 0.58
  avg_trade_return: 0.015
```

### Example 3: Data Pipeline for Live Trading

```bash
python orchestrator/run.py \
  --workflow quant \
  --task "Build real-time data pipeline for options pricing" \
  --create-pr
```

**Data Engineer output includes:**
- Pipeline architecture diagram (in text)
- Technology stack recommendations
- Performance requirements
- Data quality considerations

## Understanding the Output

### State File Structure

The `*_state.yaml` file contains the complete workflow state:

```yaml
run_id: run_engineering_20260103_092418
workflow_type: engineering
task_description: "Add logging functionality"
created_at: "2026-01-03T09:24:18.480446"
current_stage: workflow_complete
current_agent: critic
agent_outputs:
  - agent_name: planner
    timestamp: "2026-01-03T09:24:18.480575"
    summary: |
      Planning engineering workflow...
    structured_data:
      agent_name: planner
      findings: [...]
      decisions: [...]
      tasks: [...]
      next_agent: engineer
```

### Report File Structure

The `*_report.md` file provides a human-readable summary:

```markdown
# Multi-Agent Workflow Report

**Run ID**: run_engineering_20260103_092418
**Workflow Type**: engineering
**Task Description**: Add logging functionality

## Execution Timeline

### Step 1: planner
**Timestamp**: 2026-01-03T09:24:18.480575

[Summary of planner output]

### Step 2: engineer
...
```

### Agent Output Format

Each agent produces:

1. **Human-readable summary**: Plain text explanation
2. **Structured YAML**: Machine-parsable data

Example structured output:
```yaml
agent_name: "quant_researcher"
findings:
  - "Identified momentum patterns in price data"
  - "Strong correlation with volume indicators"
decisions:
  - "Use 20-day lookback period"
  - "Set stop-loss at 2%"
metrics:
  sharpe_ratio: 1.35
  max_drawdown: 0.12
tasks:
  - id: 1
    description: "Build data pipeline"
    priority: "high"
risks:
  - "Strategy may underperform in low volatility"
next_agent: "data_engineer"
```

## GitHub Integration Examples

### Example 1: Basic PR Creation

```bash
# Set token
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"

# Run with PR creation
python orchestrator/run.py \
  --workflow engineering \
  --task "Update API documentation" \
  --create-pr
```

**Result:**
```
============================================================
Pull Request Created Successfully!
============================================================
PR Number: 42
PR URL: https://github.com/owner/repo/pull/42
Branch: agent/engineering/run_engineering_20260103_092500
============================================================
```

### Example 2: PR to Different Base Branch

```bash
python orchestrator/run.py \
  --workflow quant \
  --task "Add new trading signals" \
  --create-pr \
  --base-branch develop
```

### Example 3: Setting GitHub Repository Manually

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxx"
export GITHUB_REPOSITORY="myorg/myrepo"

python orchestrator/run.py \
  --workflow engineering \
  --task "Implement rate limiting" \
  --create-pr
```

## Advanced Examples

### Example 1: Running Multiple Workflows

```bash
# Run multiple workflows in sequence
for task in "Add tests" "Update docs" "Fix linting"; do
  python orchestrator/run.py \
    --workflow engineering \
    --task "$task"
done
```

### Example 2: Automated CI/CD Integration

```bash
#!/bin/bash
# ci-workflow.sh

# Run workflow and capture exit code
python orchestrator/run.py \
  --workflow engineering \
  --task "Automated code quality improvements" \
  --create-pr

if [ $? -eq 0 ]; then
  echo "✓ Workflow completed successfully"
  exit 0
else
  echo "✗ Workflow failed"
  exit 1
fi
```

### Example 3: Custom Workflow Configuration

You can extend the framework by modifying agent behavior:

```python
# custom_workflow.py
from orchestrator.run import WorkflowOrchestrator

# Create custom orchestrator
orchestrator = WorkflowOrchestrator(
    workflow_type="engineering",
    task_description="Custom task",
    mock_mode=True
)

# Run workflow
state = orchestrator.run_workflow()

# Access state data
print(f"Completed {len(state.agent_outputs)} steps")
for output in state.agent_outputs:
    print(f"- {output['agent_name']}: {output['structured_data']['next_agent']}")
```

## Troubleshooting

### Issue: Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'agents'
```

**Solution:**
Make sure you're running from the repository root:
```bash
cd /path/to/practise
python orchestrator/run.py --workflow engineering --task "test"
```

### Issue: GitHub Token Not Found

**Problem:**
```
ValueError: GitHub token not provided
```

**Solution:**
Set the `GITHUB_TOKEN` environment variable:
```bash
export GITHUB_TOKEN="ghp_your_token_here"
python orchestrator/run.py --workflow engineering --task "test" --create-pr
```

### Issue: PR Creation Failed (422 Error)

**Problem:**
```
Failed to create PR: 422 - Validation Failed
```

**Common causes:**
1. Branch already has an open PR
2. No changes between base and head branches
3. Branch name already exists

**Solution:**
Check existing PRs and branches:
```bash
# List open PRs
gh pr list

# Check if branch exists
git branch -a | grep agent/
```

### Issue: Permission Denied

**Problem:**
```
Failed to push: Permission denied
```

**Solution:**
Ensure your GitHub token has the correct permissions:
- `repo` scope for private repositories
- `public_repo` scope for public repositories

### Issue: No Changes to Commit

**Problem:**
```
No changes to commit
```

**Explanation:**
This is normal in mock mode since no actual code changes are made. The framework demonstrates the workflow orchestration without modifying files.

To see real changes, you would:
1. Integrate with an LLM (future enhancement)
2. Or manually implement the suggested changes before running with `--create-pr`

## Best Practices

### 1. Clear Task Descriptions

❌ Bad:
```bash
python orchestrator/run.py --workflow engineering --task "fix stuff"
```

✅ Good:
```bash
python orchestrator/run.py --workflow engineering --task "Fix race condition in concurrent user session handling"
```

### 2. Review Before Creating PRs

```bash
# First run without --create-pr
python orchestrator/run.py --workflow engineering --task "Add caching"

# Review the output
cat reports/run_engineering_*_report.md

# If satisfied, run with PR creation
python orchestrator/run.py --workflow engineering --task "Add caching" --create-pr
```

### 3. Use Descriptive Workflow Types

- Use `engineering` for: bug fixes, refactoring, features, tests
- Use `quant` for: trading strategies, data analysis, backtesting, pipelines

### 4. Keep Generated Reports

While reports are gitignored by default, you may want to archive them:

```bash
# Archive completed workflow reports
mkdir -p archive
cp reports/run_*_report.md archive/
```

## Next Steps

- Read the main [README.md](README.md) for full documentation
- Explore agent implementations in `agents/` directory
- Customize prompt templates in `prompts/` directory
- Extend with LLM integration (see README for guidance)

---

For questions or issues, please refer to the repository documentation or create an issue on GitHub.
