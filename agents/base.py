"""
Base Agent class with structured output protocol validation.
"""
import yaml
import json
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class AgentOutputProtocol:
    """
    Structured output protocol for all agents.
    Each agent must output:
    1. Human-readable summary
    2. Machine-parsable structured data (YAML/JSON)
    """
    
    def __init__(self, data: Dict[str, Any]):
        self.agent_name = data.get('agent_name', '')
        self.findings = data.get('findings', [])
        self.decisions = data.get('decisions', [])
        self.tasks = data.get('tasks', [])
        self.risks = data.get('risks', [])
        self.metrics = data.get('metrics', {})
        self.next_agent = data.get('next_agent', None)
        self.raw_data = data
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'AgentOutputProtocol':
        """Parse YAML string into protocol object."""
        data = yaml.safe_load(yaml_str)
        return cls(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentOutputProtocol':
        """Parse JSON string into protocol object."""
        data = json.loads(json_str)
        return cls(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.raw_data
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that required fields are present.
        Returns (is_valid, error_message).
        """
        if not self.agent_name:
            return False, "Missing required field: agent_name"
        
        if not self.findings and not self.decisions:
            return False, "Must have either findings or decisions"
        
        return True, None


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    """
    
    def __init__(self, name: str, prompt_template: str = ""):
        self.name = name
        self.prompt_template = prompt_template
    
    @abstractmethod
    def process(self, request: Dict[str, Any], mock_mode: bool = True) -> tuple[str, AgentOutputProtocol]:
        """
        Process the request and return (summary, structured_output).
        
        Args:
            request: Input request with context and parameters
            mock_mode: If True, generate mock/rule-based output without LLM
        
        Returns:
            Tuple of (human_readable_summary, structured_protocol_object)
        """
        pass
    
    def load_prompt_template(self, template_path: str) -> str:
        """Load prompt template from file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def format_output(self, summary: str, structured_data: Dict[str, Any]) -> str:
        """
        Format output with human-readable summary and structured YAML block.
        """
        yaml_output = yaml.dump(structured_data, default_flow_style=False, allow_unicode=True)
        
        output = f"""
# Agent Output: {self.name}

## Summary
{summary}

## Structured Output (YAML)
```yaml
{yaml_output}
```
"""
        return output
