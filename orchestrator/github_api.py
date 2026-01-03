"""
GitHub API wrapper for creating pull requests using Personal Access Token.
"""
import os
import requests
from typing import Dict, Any, Optional


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class GitHubAPI:
    """
    GitHub REST API client with PAT authentication.
    """
    
    def __init__(self, token: Optional[str] = None, repo_owner: Optional[str] = None, 
                 repo_name: Optional[str] = None):
        """
        Initialize GitHub API client.
        
        Args:
            token: GitHub Personal Access Token (reads from GITHUB_TOKEN env var if not provided)
            repo_owner: Repository owner (reads from GITHUB_REPOSITORY env var if not provided)
            repo_name: Repository name (reads from GITHUB_REPOSITORY env var if not provided)
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        
        if not self.token:
            raise ValueError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable or pass token parameter."
            )
        
        # Parse repo owner and name from GITHUB_REPOSITORY env var if not provided
        if not repo_owner or not repo_name:
            github_repo = os.environ.get('GITHUB_REPOSITORY', '')
            if '/' in github_repo:
                parts = github_repo.split('/')
                repo_owner = repo_owner or parts[0]
                repo_name = repo_name or parts[1]
        
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        
        if not self.repo_owner or not self.repo_name:
            raise ValueError(
                "Repository owner and name not provided. Set GITHUB_REPOSITORY environment variable "
                "or pass repo_owner and repo_name parameters."
            )
        
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
        }
    
    def create_pull_request(self, title: str, body: str, head: str, base: str = "main") -> Dict[str, Any]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head: Branch name containing the changes
            base: Base branch (default: "main")
        
        Returns:
            Pull request data from GitHub API
        
        Raises:
            GitHubAPIError: If API request fails
        """
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"
        
        data = {
            'title': title,
            'body': body,
            'head': head,
            'base': base,
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            error_msg = f"Failed to create PR: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('message', '')}"
            except:
                error_msg += f" - {response.text}"
            
            raise GitHubAPIError(error_msg)
    
    def get_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details.
        
        Args:
            pr_number: Pull request number
        
        Returns:
            Pull request data
        """
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise GitHubAPIError(f"Failed to get PR: {response.status_code}")
    
    def update_pull_request(self, pr_number: int, title: Optional[str] = None, 
                           body: Optional[str] = None, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a pull request.
        
        Args:
            pr_number: Pull request number
            title: New title (optional)
            body: New description (optional)
            state: New state: "open" or "closed" (optional)
        
        Returns:
            Updated pull request data
        """
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        
        data = {}
        if title is not None:
            data['title'] = title
        if body is not None:
            data['body'] = body
        if state is not None:
            data['state'] = state
        
        response = requests.patch(url, json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise GitHubAPIError(f"Failed to update PR: {response.status_code}")
    
    def list_pull_requests(self, state: str = "open", base: Optional[str] = None) -> list:
        """
        List pull requests.
        
        Args:
            state: "open", "closed", or "all"
            base: Filter by base branch (optional)
        
        Returns:
            List of pull request data
        """
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"
        params = {'state': state}
        if base:
            params['base'] = base
        
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise GitHubAPIError(f"Failed to list PRs: {response.status_code}")
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get repository information.
        
        Returns:
            Repository data
        """
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise GitHubAPIError(f"Failed to get repository info: {response.status_code}")
