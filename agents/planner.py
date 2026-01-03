"""
Planner Agent - Creates execution plans and task breakdowns.
"""
from typing import Dict, Any
from agents.base import BaseAgent, AgentOutputProtocol


class PlannerAgent(BaseAgent):
    """
    Planner agent creates high-level execution plans for workflows.
    """
    
    def __init__(self):
        super().__init__(name="planner")
    
    def process(self, request: Dict[str, Any], mock_mode: bool = True) -> tuple[str, AgentOutputProtocol]:
        """
        Generate execution plan based on the workflow type.
        
        In mock mode, generates a rule-based plan.
        """
        workflow_type = request.get('workflow_type', 'engineering')
        task_description = request.get('task_description', 'No task specified')
        
        if mock_mode:
            return self._mock_process(workflow_type, task_description)
        else:
            # Future: Real LLM integration
            raise NotImplementedError("LLM mode not yet implemented")
    
    def _mock_process(self, workflow_type: str, task_description: str) -> tuple[str, AgentOutputProtocol]:
        """Generate mock plan output."""
        
        if workflow_type == 'quant':
            summary = f"""
Planning quantitative research workflow for: {task_description}

The plan includes:
1. Data collection and preprocessing
2. Feature engineering and analysis
3. Strategy backtesting
4. Performance evaluation
"""
            
            structured_data = {
                'agent_name': 'planner',
                'findings': [
                    'Identified need for historical market data',
                    'Strategy requires multi-factor analysis',
                ],
                'decisions': [
                    'Use quant_researcher for data analysis',
                    'Then data_engineer for pipeline setup',
                    'Finally engineer for implementation',
                ],
                'tasks': [
                    {
                        'id': 1,
                        'description': 'Analyze data requirements',
                        'assigned_to': 'quant_researcher',
                    },
                    {
                        'id': 2,
                        'description': 'Build data pipeline',
                        'assigned_to': 'data_engineer',
                    },
                    {
                        'id': 3,
                        'description': 'Implement strategy code',
                        'assigned_to': 'engineer',
                    },
                ],
                'risks': [
                    'Data quality issues may affect results',
                    'Overfitting in strategy parameters',
                ],
                'next_agent': 'quant_researcher',
            }
        
        else:  # engineering workflow
            summary = f"""
Planning engineering workflow for: {task_description}

The plan includes:
1. Code review and issue analysis
2. Implementation of changes
3. Testing and validation
4. Documentation updates
"""
            
            structured_data = {
                'agent_name': 'planner',
                'findings': [
                    'Identified engineering task requiring code changes',
                    'Changes should follow existing patterns',
                ],
                'decisions': [
                    'Use engineer for implementation',
                    'Then critic for code review',
                ],
                'tasks': [
                    {
                        'id': 1,
                        'description': 'Implement code changes',
                        'assigned_to': 'engineer',
                    },
                    {
                        'id': 2,
                        'description': 'Review and validate',
                        'assigned_to': 'critic',
                    },
                ],
                'risks': [
                    'Breaking changes may affect existing functionality',
                ],
                'next_agent': 'engineer',
            }
        
        protocol = AgentOutputProtocol(structured_data)
        return summary, protocol
