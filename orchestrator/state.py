"""
State management for multi-agent workflow execution.
"""
import yaml
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class WorkflowState:
    """
    Manages workflow execution state including agent outputs and progress.
    """
    
    def __init__(self, run_id: str, workflow_type: str, task_description: str):
        self.run_id = run_id
        self.workflow_type = workflow_type
        self.task_description = task_description
        self.created_at = datetime.now().isoformat()
        self.current_stage = "initialized"
        self.current_agent = None
        self.agent_outputs = []
        self.metadata = {}
    
    def add_agent_output(self, agent_name: str, summary: str, structured_data: Dict[str, Any]):
        """Add output from an agent."""
        output = {
            'agent_name': agent_name,
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'structured_data': structured_data,
        }
        self.agent_outputs.append(output)
        self.current_agent = agent_name
    
    def update_stage(self, stage: str):
        """Update the current workflow stage."""
        self.current_stage = stage
        self.metadata['last_updated'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            'run_id': self.run_id,
            'workflow_type': self.workflow_type,
            'task_description': self.task_description,
            'created_at': self.created_at,
            'current_stage': self.current_stage,
            'current_agent': self.current_agent,
            'agent_outputs': self.agent_outputs,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Create state from dictionary."""
        state = cls(
            run_id=data['run_id'],
            workflow_type=data['workflow_type'],
            task_description=data['task_description']
        )
        state.created_at = data['created_at']
        state.current_stage = data['current_stage']
        state.current_agent = data.get('current_agent')
        state.agent_outputs = data.get('agent_outputs', [])
        state.metadata = data.get('metadata', {})
        return state


class StateManager:
    """
    Manages reading and writing workflow state to disk.
    """
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
    
    def save_state(self, state: WorkflowState, format: str = "yaml"):
        """
        Save workflow state to file.
        
        Args:
            state: WorkflowState object to save
            format: "yaml" or "json"
        """
        filename = f"{state.run_id}_state.{format}"
        filepath = self.reports_dir / filename
        
        data = state.to_dict()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if format == "yaml":
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_state(self, run_id: str, format: str = "yaml") -> Optional[WorkflowState]:
        """
        Load workflow state from file.
        
        Args:
            run_id: Run ID to load
            format: "yaml" or "json"
        
        Returns:
            WorkflowState object or None if not found
        """
        filename = f"{run_id}_state.{format}"
        filepath = self.reports_dir / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if format == "yaml":
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return WorkflowState.from_dict(data)
    
    def save_report(self, state: WorkflowState, content: str):
        """
        Save a human-readable report of the workflow execution.
        """
        filename = f"{state.run_id}_report.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def generate_report(self, state: WorkflowState) -> str:
        """
        Generate a human-readable markdown report from workflow state.
        """
        report = f"""# Multi-Agent Workflow Report

**Run ID**: {state.run_id}
**Workflow Type**: {state.workflow_type}
**Task Description**: {state.task_description}
**Created At**: {state.created_at}
**Current Stage**: {state.current_stage}

---

## Execution Timeline

"""
        
        for i, output in enumerate(state.agent_outputs, 1):
            report += f"""
### Step {i}: {output['agent_name']}
**Timestamp**: {output['timestamp']}

{output['summary']}

**Structured Output**:
```yaml
{yaml.dump(output['structured_data'], default_flow_style=False, allow_unicode=True)}
```

---
"""
        
        return report
