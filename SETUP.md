# Setup Instructions

## Automated README Updates

This repository uses GitHub Actions to automatically update the README with the latest skills from configured marketplaces.

### Setting up the Personal Access Token

To allow the automated workflow to push changes to the main branch, you need to create a Personal Access Token (PAT) with repository permissions:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Awesome Claude Skills Update"
4. Select the following scopes:
   - `repo` (Full control of private repositories) - OR for public repos:
   - `public_repo` (Access public repositories)
5. Click "Generate token"
6. Copy the token immediately (you won't be able to see it again)

### Adding the Token to Repository Secrets

1. Go to your repository settings
2. Navigate to "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Name: `SKILL_UPDATE_TOKEN`
5. Value: Paste your personal access token
6. Click "Add secret"

### Workflow Behavior

The workflow runs hourly and will:
- Fetch the latest skills from configured marketplaces
- Update the README.md if changes are detected
- Commit and push the changes automatically

### Troubleshooting

If the workflow fails with permission errors:
- Verify the `SKILL_UPDATE_TOKEN` secret is set correctly
- Ensure the token has the required permissions
- Check that the token hasn't expired

### Manual Testing

You can trigger the workflow manually from the Actions tab or by dispatching it via the GitHub CLI:

```bash
gh workflow run "Update Skills README"
```