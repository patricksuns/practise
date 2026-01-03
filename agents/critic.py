"""
Critic Agent - Reviews code and provides feedback.
"""
from typing import Dict, Any
from agents.base import BaseAgent, AgentOutputProtocol


class CriticAgent(BaseAgent):
    """
    Critic reviews code, identifies issues, and provides feedback.
    """
    
    def __init__(self):
        super().__init__(name="critic")
    
    def process(self, request: Dict[str, Any], mock_mode: bool = True) -> tuple[str, AgentOutputProtocol]:
        """
        Review code and provide feedback.
        """
        if mock_mode:
            return self._mock_process(request)
        else:
            raise NotImplementedError("LLM mode not yet implemented")
    
    def _mock_process(self, request: Dict[str, Any]) -> tuple[str, AgentOutputProtocol]:
        """Generate mock code review output."""
        
        summary = """
Code Review Complete

Overall Assessment: APPROVED with minor suggestions

Strengths:
✓ Code follows project conventions and style guidelines
✓ Comprehensive test coverage (>90%)
✓ Good error handling and input validation
✓ Clear documentation and comments
✓ Proper use of type hints

Minor Suggestions:
- Consider adding more edge case tests
- Some functions could benefit from additional docstrings
- Monitor performance under high load in production

Security Review:
✓ No hardcoded credentials
✓ Input sanitization implemented
✓ No SQL injection vulnerabilities
✓ Proper error message handling (no sensitive data leaks)

Performance Review:
✓ Efficient algorithms used
✓ No obvious bottlenecks
- Consider caching for frequently accessed data

Recommendation:
Code is ready to merge. The implementation is solid and meets all requirements.
PR can be created.
"""
        
        structured_data = {
            'agent_name': 'critic',
            'findings': [
                'Code quality is high',
                'Test coverage exceeds 90%',
                'No critical issues found',
                'Minor improvements possible but not blocking',
            ],
            'decisions': [
                'Approve code for merge',
                'Minor suggestions can be addressed in future PRs',
                'Ready to create pull request',
            ],
            'tasks': [
                {
                    'id': 1,
                    'description': 'Create pull request',
                    'status': 'ready',
                },
            ],
            'risks': [
                'None identified - code is production-ready',
            ],
            'metrics': {
                'code_quality_score': 8.5,
                'test_coverage': 0.92,
                'complexity_score': 6.2,
            },
            'next_agent': None,  # End of workflow
        }
        
        protocol = AgentOutputProtocol(structured_data)
        return summary, protocol
