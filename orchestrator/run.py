#!/usr/bin/env python3
"""
Multi-Agent Runner - CLI entry point for workflow orchestration.
"""
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.state import WorkflowState, StateManager
from orchestrator.github_api import GitHubAPI, GitHubAPIError
from orchestrator.git_ops import GitOps, GitOperationError
from agents import (
    PlannerAgent, QuantResearcherAgent, DataEngineerAgent,
    EngineerAgent, CriticAgent, AgentOutputProtocol
)


class WorkflowOrchestrator:
    """
    Orchestrates multi-agent workflows.
    """
    
    def __init__(self, workflow_type: str, task_description: str, mock_mode: bool = True):
        self.workflow_type = workflow_type
        self.task_description = task_description
        self.mock_mode = mock_mode
        
        # Generate run ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{workflow_type}_{timestamp}"
        
        # Initialize state
        self.state = WorkflowState(self.run_id, workflow_type, task_description)
        self.state_manager = StateManager()
        
        # Initialize agents
        self.agents = {
            'planner': PlannerAgent(),
            'quant_researcher': QuantResearcherAgent(),
            'data_engineer': DataEngineerAgent(),
            'engineer': EngineerAgent(),
            'critic': CriticAgent(),
        }
    
    def run_workflow(self) -> WorkflowState:
        """
        Execute the complete workflow.
        """
        print(f"\n{'='*60}")
        print(f"Starting Multi-Agent Workflow")
        print(f"{'='*60}")
        print(f"Run ID: {self.run_id}")
        print(f"Workflow Type: {self.workflow_type}")
        print(f"Task: {self.task_description}")
        print(f"Mode: {'Mock' if self.mock_mode else 'LLM'}")
        print(f"{'='*60}\n")
        
        # Start with planner
        current_agent_name = 'planner'
        request = {
            'workflow_type': self.workflow_type,
            'task_description': self.task_description,
        }
        
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while current_agent_name and iteration < max_iterations:
            iteration += 1
            
            print(f"\n--- Step {iteration}: Running {current_agent_name} ---\n")
            
            # Get the agent
            agent = self.agents.get(current_agent_name)
            if not agent:
                print(f"Error: Unknown agent '{current_agent_name}'")
                break
            
            # Process with agent
            try:
                summary, protocol = agent.process(request, mock_mode=self.mock_mode)
                
                # Validate output
                is_valid, error = protocol.validate()
                if not is_valid:
                    print(f"Error: Invalid agent output - {error}")
                    break
                
                # Save agent output to state
                self.state.add_agent_output(current_agent_name, summary, protocol.to_dict())
                self.state.update_stage(f"completed_{current_agent_name}")
                
                # Print summary
                print(f"Agent: {current_agent_name}")
                print(f"Summary:\n{summary}")
                print(f"\nNext Agent: {protocol.next_agent}")
                
                # Save state after each agent
                self.state_manager.save_state(self.state)
                
                # Move to next agent
                current_agent_name = protocol.next_agent
                
                # Update request with previous output for context
                request['previous_output'] = protocol.to_dict()
                
            except Exception as e:
                print(f"Error running agent {current_agent_name}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        if iteration >= max_iterations:
            print(f"\nWarning: Reached maximum iterations ({max_iterations})")
        
        # Mark workflow as complete
        self.state.update_stage("workflow_complete")
        self.state_manager.save_state(self.state)
        
        # Generate and save report
        report = self.state_manager.generate_report(self.state)
        report_path = self.state_manager.save_report(self.state, report)
        
        print(f"\n{'='*60}")
        print(f"Workflow Complete!")
        print(f"{'='*60}")
        print(f"Run ID: {self.run_id}")
        print(f"Total Steps: {iteration}")
        print(f"State saved to: {self.state_manager.reports_dir / f'{self.run_id}_state.yaml'}")
        print(f"Report saved to: {report_path}")
        print(f"{'='*60}\n")
        
        return self.state


def create_pull_request(state: WorkflowState, git_ops: GitOps, github_api: GitHubAPI, 
                       base_branch: str = "main") -> Optional[Dict[str, Any]]:
    """
    Create a pull request for the workflow results.
    
    Args:
        state: Workflow state
        git_ops: GitOps instance
        github_api: GitHubAPI instance
        base_branch: Base branch for PR (default: "main")
    
    Returns:
        PR data from GitHub API or None if creation fails
    """
    try:
        print(f"\n{'='*60}")
        print(f"Creating Pull Request")
        print(f"{'='*60}\n")
        
        # Create branch name
        branch_name = f"agent/{state.workflow_type}/{state.run_id}"
        
        print(f"Creating branch: {branch_name}")
        git_ops.create_branch(branch_name, from_branch=base_branch)
        
        # Check if there are changes to commit
        if git_ops.has_changes():
            print("Adding and committing changes...")
            git_ops.add_files()
            commit_msg = f"Multi-agent workflow: {state.task_description}\n\nRun ID: {state.run_id}"
            commit_hash = git_ops.commit(commit_msg)
            print(f"Committed: {commit_hash}")
        else:
            print("No changes to commit")
        
        # Push branch
        print(f"Pushing branch to remote...")
        git_ops.push(branch_name)
        
        # Create PR
        pr_title = f"[{state.workflow_type.upper()}] {state.task_description}"
        
        # Generate PR body from workflow state
        pr_body = f"""# Multi-Agent Workflow Results

**Run ID**: {state.run_id}
**Workflow Type**: {state.workflow_type}
**Task**: {state.task_description}

## Execution Summary

"""
        
        for i, output in enumerate(state.agent_outputs, 1):
            agent_name = output['agent_name']
            pr_body += f"### {i}. {agent_name}\n\n"
            pr_body += f"{output['summary']}\n\n"
        
        pr_body += f"""
## Details

Full execution report available in: `reports/{state.run_id}_report.md`

---
*Generated by Multi-Agent Runner*
"""
        
        print(f"Creating pull request...")
        pr = github_api.create_pull_request(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base=base_branch
        )
        
        print(f"\n{'='*60}")
        print(f"Pull Request Created Successfully!")
        print(f"{'='*60}")
        print(f"PR Number: {pr['number']}")
        print(f"PR URL: {pr['html_url']}")
        print(f"Branch: {branch_name}")
        print(f"{'='*60}\n")
        
        return pr
        
    except (GitOperationError, GitHubAPIError) as e:
        print(f"Error creating pull request: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Multi-Agent Runner for quantitative research and engineering automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run engineering workflow in mock mode
  python orchestrator/run.py --workflow engineering --task "Refactor error handling"
  
  # Run quant workflow in mock mode
  python orchestrator/run.py --workflow quant --task "Develop momentum strategy"
  
  # Run with PR creation
  python orchestrator/run.py --workflow engineering --task "Add logging" --create-pr
  
Environment Variables:
  GITHUB_TOKEN      GitHub Personal Access Token (required for --create-pr)
  GITHUB_REPOSITORY Repository in format "owner/repo" (default: auto-detected)
        """
    )
    
    parser.add_argument(
        '--workflow',
        type=str,
        choices=['engineering', 'quant'],
        required=True,
        help='Workflow type to execute'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        required=True,
        help='Task description for the workflow'
    )
    
    parser.add_argument(
        '--mock-mode',
        action='store_true',
        default=True,
        help='Use mock mode (rule-based outputs without LLM) - default'
    )
    
    parser.add_argument(
        '--llm-mode',
        action='store_true',
        help='Use LLM mode (requires LLM integration)'
    )
    
    parser.add_argument(
        '--create-pr',
        action='store_true',
        help='Create a pull request after workflow completion'
    )
    
    parser.add_argument(
        '--base-branch',
        type=str,
        default='main',
        help='Base branch for pull request (default: main)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    mock_mode = not args.llm_mode
    
    # Create orchestrator and run workflow
    orchestrator = WorkflowOrchestrator(
        workflow_type=args.workflow,
        task_description=args.task,
        mock_mode=mock_mode
    )
    
    state = orchestrator.run_workflow()
    
    # Create PR if requested
    if args.create_pr:
        try:
            git_ops = GitOps()
            github_api = GitHubAPI()
            create_pull_request(state, git_ops, github_api, args.base_branch)
        except Exception as e:
            print(f"Failed to create PR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print("\n✓ Workflow completed successfully!\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
