# gitlab2jira
Gitlab 2 jira migration 
Got it! Below is the updated Python script where:

1. **Configuration is loaded in a method** (`load_config`).
2. **Dry run mode, GitLab project ID, and GitLab group ID are passed as CLI parameters** using `argparse`.

This makes the script more flexible and easier to use without modifying the `config.yaml` file for every run.

---

### **Updated `config.yaml` File**

```yaml
# GitLab Configuration
gitlab:
  url: "https://gitlab.com/api/v4"
  token: "<your_gitlab_token>"

# Jira Configuration
jira:
  url: "https://<your_domain>.atlassian.net/rest/api/3"
  project_key: "<your_jira_project_key>"
  email: "<your_email>"
  token: "<your_jira_token>"
  issue_type: "Task"  # Default issue type
  epic_issue_type: "Epic"  # Issue type for epics
  epic_name_field_id: "customfield_12345"  # Custom field ID for epic name

# Field Mappings
field_mappings:
  title: "summary"
  description: "description"
  labels: "labels"
  milestone: "fixVersion"
  assignee: "assignee"
```

---

### **Updated Python Script**

```python
import requests
import yaml
import json
import argparse

# Helper functions
def log(message):
    print(f"[LOG] {message}")

def load_config(config_file):
    """Load configuration from YAML file."""
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def fetch_gitlab_issues(gitlab_url, project_id, headers):
    """Fetch all issues from GitLab."""
    url = f"{gitlab_url}/projects/{project_id}/issues"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_gitlab_epics(gitlab_url, group_id, headers):
    """Fetch all epics from GitLab."""
    url = f"{gitlab_url}/groups/{group_id}/epics"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def map_gitlab_to_jira(gitlab_issue, issue_type, field_mappings):
    """Map GitLab issue fields to Jira fields."""
    jira_issue = {
        "fields": {
            "project": {"key": config["jira"]["project_key"]},
            "issuetype": {"name": issue_type},
        }
    }
    for gitlab_field, jira_field in field_mappings.items():
        if gitlab_field in gitlab_issue:
            jira_issue["fields"][jira_field] = gitlab_issue[gitlab_field]
    return jira_issue

def create_jira_issue(issue, jira_url, headers, auth, dry_run):
    """Create an issue in Jira."""
    if dry_run:
        log(f"DRY RUN: Would create issue: {json.dumps(issue, indent=2)}")
        return {"key": "DRY-RUN-KEY"}
    else:
        url = f"{jira_url}/issue"
        response = requests.post(url, json=issue, headers=headers, auth=auth)
        response.raise_for_status()
        return response.json()

def migrate_issues(config, gitlab_project_id, dry_run):
    """Migrate issues from GitLab to Jira."""
    log("Fetching issues from GitLab...")
    gitlab_issues = fetch_gitlab_issues(config["gitlab"]["url"], gitlab_project_id, {"PRIVATE-TOKEN": config["gitlab"]["token"]})
    log(f"Found {len(gitlab_issues)} issues.")

    for gitlab_issue in gitlab_issues:
        log(f"Processing issue: {gitlab_issue['title']} (ID: {gitlab_issue['id']})")
        jira_issue = map_gitlab_to_jira(gitlab_issue, config["jira"]["issue_type"], config["field_mappings"])
        create_jira_issue(jira_issue, config["jira"]["url"], {"Content-Type": "application/json"}, (config["jira"]["email"], config["jira"]["token"]), dry_run)

def migrate_epics(config, gitlab_group_id, dry_run):
    """Migrate epics from GitLab to Jira."""
    log("Fetching epics from GitLab...")
    gitlab_epics = fetch_gitlab_epics(config["gitlab"]["url"], gitlab_group_id, {"PRIVATE-TOKEN": config["gitlab"]["token"]})
    log(f"Found {len(gitlab_epics)} epics.")

    for gitlab_epic in gitlab_epics:
        log(f"Processing epic: {gitlab_epic['title']} (ID: {gitlab_epic['id']})")
        jira_epic = map_gitlab_to_jira(gitlab_epic, config["jira"]["epic_issue_type"], config["field_mappings"])
        jira_epic["fields"][config["jira"]["epic_name_field_id"]] = gitlab_epic["title"]  # Set epic name
        create_jira_issue(jira_epic, config["jira"]["url"], {"Content-Type": "application/json"}, (config["jira"]["email"], config["jira"]["token"]), dry_run)

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
    config = load_config(args.config)

    # Start migration
    log("Starting migration...")
    migrate_issues(config, args.gitlab_project_id, args.dry_run)
    migrate_epics(config, args.gitlab_group_id, args.dry_run)
    log("Migration complete.")
```

---

### **How It Works**
1. **CLI Parameters**:
   - `--config`: Path to the `config.yaml` file.
   - `--gitlab-project-id`: GitLab project ID for fetching issues.
   - `--gitlab-group-id`: GitLab group ID for fetching epics.
   - `--dry-run`: Enables dry run mode (no changes are made to Jira).

2. **Configuration Loading**:
   - The `load_config` method reads the `config.yaml` file and returns the configuration as a dictionary.

3. **Dry Run Mode**:
   - When `--dry-run` is passed, the script logs the payload that would be sent to Jira without making any API calls.

4. **Field Mappings**:
   - The `field_mappings` section in the YAML file defines how GitLab fields are mapped to Jira fields.

5. **Custom Fields**:
   - The `epic_name_field_id` parameter specifies the custom field ID for the epic name in Jira.

---

### **How to Use**
1. Create a `config.yaml` file with the provided template and fill in the required values.
2. Run the script with CLI parameters:
   ```bash
   python migrate_gitlab_to_jira.py \
     --config config.yaml \
     --gitlab-project-id 12345 \
     --gitlab-group-id 67890 \
     --dry-run
   ```
3. Review the logs to ensure the data is correctly mapped.
4. Remove the `--dry-run` flag to perform the actual migration:
   ```bash
   python migrate_gitlab_to_jira.py \
     --config config.yaml \
     --gitlab-project-id 12345 \
     --gitlab-group-id 67890
   ```

---

### **Example Output (Dry Run Mode)**
```
[LOG] Starting migration...
[LOG] Fetching issues from GitLab...
[LOG] Found 10 issues.
[LOG] Processing issue: Bug in login page (ID: 123)
[LOG] DRY RUN: Would create issue: {
  "fields": {
    "project": {
      "key": "PROJ"
    },
    "issuetype": {
      "name": "Task"
    },
    "summary": "Bug in login page",
    "description": "The login page crashes on Safari.",
    "labels": ["bug", "ui"]
  }
}
[LOG] Migration complete.
```

---

### **Next Steps**
- Add error handling for API failures.
- Handle pagination for large datasets.
- Add support for attachments and comments if needed.

Let me know if you need further assistance!
