import requests
import yaml
import json
import argparse
from datetime import datetime

# Helper function
def log(message):
    print(f"[LOG] {message}")

# GitLab API Client
class GitLabClient:
    def __init__(self, url, token):
        self.url = url
        self.headers = {"PRIVATE-TOKEN": token}

    def fetch_issues(self, project_id, state="all"):
        """Fetch issues from a GitLab project."""
        url = f"{self.url}/projects/{project_id}/issues"
        params = {"state": state} if state != "all" else {}
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_epics(self, group_id):
        """Fetch epics from a GitLab group."""
        url = f"{self.url}/groups/{group_id}/epics"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_issue_comments(self, project_id, issue_iid):
        """Fetch comments for a GitLab issue."""
        url = f"{self.url}/projects/{project_id}/issues/{issue_iid}/notes"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Jira API Client
class JiraClient:
    def __init__(self, url, email, token):
        self.url = url
        self.auth = (email, token)
        self.headers = {"Content-Type": "application/json"}

    def create_issue(self, issue, dry_run=False):
        """Create an issue in Jira."""
        if dry_run:
            log(f"DRY RUN: Would create issue: {json.dumps(issue, indent=2)}")
            return {"key": "DRY-RUN-KEY"}
        else:
            url = f"{self.url}/issue"
            response = requests.post(url, json=issue, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            return response.json()

    def create_comment(self, issue_key, comment, dry_run=False):
        """Create a comment on a Jira issue."""
        if dry_run:
            log(f"DRY RUN: Would create comment on issue {issue_key}: {json.dumps(comment, indent=2)}")
        else:
            url = f"{self.url}/issue/{issue_key}/comment"
            response = requests.post(url, json=comment, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            return response.json()

    def transition_issue(self, issue_key, status, dry_run=False):
        """Transition a Jira issue to a specific status."""
        if dry_run:
            log(f"DRY RUN: Would transition issue {issue_key} to status: {status}")
        else:
            # Get available transitions for the issue
            transitions_url = f"{self.url}/issue/{issue_key}/transitions"
            response = requests.get(transitions_url, headers=self.headers, auth=self.auth)
            response.raise_for_status()
            transitions = response.json()["transitions"]

            # Find the transition ID for the target status
            transition_id = None
            for transition in transitions:
                if transition["to"]["name"].lower() == status.lower():
                    transition_id = transition["id"]
                    break

            if not transition_id:
                log(f"Error: No transition found for status {status}")
                return

            # Perform the transition
            transition_url = f"{self.url}/issue/{issue_key}/transitions"
            payload = {"transition": {"id": transition_id}}
            response = requests.post(transition_url, json=payload, headers=self.headers, auth=self.auth)
            response.raise_for_status()

# Migration Logic
class GitLabToJiraMigrator:
    def __init__(self, config, gitlab_project_id, gitlab_group_id, dry_run=False):
        self.config = config
        self.dry_run = dry_run

        # Initialize clients
        self.gitlab = GitLabClient(config["gitlab"]["url"], config["gitlab"]["token"])
        self.jira = JiraClient(config["jira"]["url"], config["jira"]["email"], config["jira"]["token"])

        # IDs
        self.gitlab_project_id = gitlab_project_id
        self.gitlab_group_id = gitlab_group_id

    def map_gitlab_to_jira(self, gitlab_issue, issue_type):
        """Map GitLab issue fields to Jira fields."""
        jira_issue = {
            "fields": {
                "project": {"key": self.config["jira"]["project_key"]},
                "issuetype": {"name": issue_type},
            }
        }
        for gitlab_field, jira_field in self.config["field_mappings"].items():
            if gitlab_field in gitlab_issue:
                jira_issue["fields"][jira_field] = gitlab_issue[gitlab_field]
        return jira_issue

    def migrate_issues(self):
        """Migrate issues and comments from GitLab to Jira."""
        log("Fetching issues from GitLab...")
        gitlab_issues = self.gitlab.fetch_issues(self.gitlab_project_id, state="all")
        log(f"Found {len(gitlab_issues)} issues.")

        for gitlab_issue in gitlab_issues:
            log(f"Processing issue: {gitlab_issue['title']} (ID: {gitlab_issue['id']}, State: {gitlab_issue['state']})")
            jira_issue = self.map_gitlab_to_jira(gitlab_issue, self.config["jira"]["issue_type"])
            jira_issue_response = self.jira.create_issue(jira_issue, self.dry_run)
            jira_issue_key = jira_issue_response["key"]

            # Transition issue based on GitLab state
            gitlab_state = gitlab_issue["state"]
            jira_status = self.config["jira"]["status_mappings"].get(gitlab_state)
            if jira_status:
                self.jira.transition_issue(jira_issue_key, jira_status, self.dry_run)

            # Migrate comments
            log(f"Fetching comments for issue: {gitlab_issue['title']} (ID: {gitlab_issue['id']})")
            gitlab_comments = self.gitlab.fetch_issue_comments(self.gitlab_project_id, gitlab_issue["iid"])
            log(f"Found {len(gitlab_comments)} comments.")

            for comment in gitlab_comments:
                jira_comment = {
                    "body": f"{comment['author']['name']} commented on {comment['created_at']}:\n\n{comment['body']}"
                }
                self.jira.create_comment(jira_issue_key, jira_comment, self.dry_run)

    def migrate_epics(self):
        """Migrate epics from GitLab to Jira."""
        log("Fetching epics from GitLab...")
        gitlab_epics = self.gitlab.fetch_epics(self.gitlab_group_id)
        log(f"Found {len(gitlab_epics)} epics.")

        for gitlab_epic in gitlab_epics:
            log(f"Processing epic: {gitlab_epic['title']} (ID: {gitlab_epic['id']})")
            jira_epic = self.map_gitlab_to_jira(gitlab_epic, self.config["jira"]["epic_issue_type"])
            jira_epic["fields"][self.config["jira"]["epic_name_field_id"]] = gitlab_epic["title"]  # Set epic name
            self.jira.create_issue(jira_epic, self.dry_run)

# Main script
if __name__ == "__main__":
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Migrate GitLab issues and epics to Jira.")
    parser.add_argument("--config", required=True, help="Path to config.yaml file.")
    parser.add_argument("--gitlab-project-id", required=True, help="GitLab project ID for issues.")
    parser.add_argument("--gitlab-group-id", required=True, help="GitLab group ID for epics.")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode.")
    args = parser.parse_args()

    # Load configuration
    with open(args.config, "r") as config_file:
        config = yaml.safe_load(config_file)

    # Start migration
    log("Starting migration...")
    migrator = GitLabToJiraMigrator(config, args.gitlab_project_id, args.gitlab_group_id, args.dry_run)
    migrator.migrate_issues()
    migrator.migrate_epics()
    log("Migration complete.")
