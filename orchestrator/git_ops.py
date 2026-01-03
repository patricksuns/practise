"""
Git operations for branch creation, commits, and push.
"""
import subprocess
from typing import Optional, List
from pathlib import Path


class GitOperationError(Exception):
    """Custom exception for git operation errors."""
    pass


class GitOps:
    """
    Handles local git operations.
    """
    
    def __init__(self, repo_path: str = "."):
        """
        Initialize GitOps.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = Path(repo_path).resolve()
    
    def _run_command(self, command: List[str]) -> tuple[int, str, str]:
        """
        Run a git command.
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    
    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        returncode, stdout, stderr = self._run_command(['git', 'branch', '--show-current'])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to get current branch: {stderr}")
        
        return stdout.strip()
    
    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> str:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            from_branch: Branch to create from (default: current branch)
        
        Returns:
            Name of the created branch
        """
        # Check if branch already exists
        returncode, stdout, stderr = self._run_command(['git', 'branch', '--list', branch_name])
        
        if stdout.strip():
            # Branch exists, check it out
            returncode, stdout, stderr = self._run_command(['git', 'checkout', branch_name])
            if returncode != 0:
                raise GitOperationError(f"Failed to checkout existing branch: {stderr}")
            return branch_name
        
        # Create new branch
        if from_branch:
            command = ['git', 'checkout', '-b', branch_name, from_branch]
        else:
            command = ['git', 'checkout', '-b', branch_name]
        
        returncode, stdout, stderr = self._run_command(command)
        
        if returncode != 0:
            raise GitOperationError(f"Failed to create branch: {stderr}")
        
        return branch_name
    
    def checkout_branch(self, branch_name: str) -> str:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout
        
        Returns:
            Name of the checked out branch
        """
        returncode, stdout, stderr = self._run_command(['git', 'checkout', branch_name])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to checkout branch: {stderr}")
        
        return branch_name
    
    def add_files(self, files: Optional[List[str]] = None):
        """
        Add files to staging area.
        
        Args:
            files: List of file paths to add (default: add all changes)
        """
        if files:
            command = ['git', 'add'] + files
        else:
            command = ['git', 'add', '.']
        
        returncode, stdout, stderr = self._run_command(command)
        
        if returncode != 0:
            raise GitOperationError(f"Failed to add files: {stderr}")
    
    def commit(self, message: str) -> str:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
        
        Returns:
            Commit hash
        """
        returncode, stdout, stderr = self._run_command(['git', 'commit', '-m', message])
        
        if returncode != 0:
            # Check if there's nothing to commit
            if "nothing to commit" in stdout or "nothing to commit" in stderr:
                return ""
            raise GitOperationError(f"Failed to commit: {stderr}")
        
        # Get the commit hash
        returncode, stdout, stderr = self._run_command(['git', 'rev-parse', 'HEAD'])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to get commit hash: {stderr}")
        
        return stdout.strip()
    
    def push(self, branch_name: Optional[str] = None, set_upstream: bool = True) -> str:
        """
        Push commits to remote.
        
        Args:
            branch_name: Branch to push (default: current branch)
            set_upstream: Set upstream tracking (default: True)
        
        Returns:
            Output from git push
        """
        if not branch_name:
            branch_name = self.get_current_branch()
        
        if set_upstream:
            command = ['git', 'push', '-u', 'origin', branch_name]
        else:
            command = ['git', 'push', 'origin', branch_name]
        
        returncode, stdout, stderr = self._run_command(command)
        
        if returncode != 0:
            raise GitOperationError(f"Failed to push: {stderr}")
        
        return stdout + stderr  # git push outputs to stderr
    
    def get_status(self) -> str:
        """Get git status."""
        returncode, stdout, stderr = self._run_command(['git', 'status'])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to get status: {stderr}")
        
        return stdout
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        returncode, stdout, stderr = self._run_command(['git', 'status', '--porcelain'])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to check for changes: {stderr}")
        
        return bool(stdout.strip())
    
    def get_remote_url(self, remote: str = "origin") -> str:
        """Get the URL of a remote."""
        returncode, stdout, stderr = self._run_command(['git', 'remote', 'get-url', remote])
        
        if returncode != 0:
            raise GitOperationError(f"Failed to get remote URL: {stderr}")
        
        return stdout.strip()
