# Setup Instructions

## Automated README Updates

This repository uses GitHub Actions to automatically update the README with the latest skills from configured marketplaces.

### Optional: Personal Access Token for Push Permissions

By default, the workflow uses `GITHUB_TOKEN` which has limited permissions in public repositories. To enable automatic pushing to the main branch, you can optionally set up a Personal Access Token:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Awesome Claude Skills Update"
4. Select the following scopes:
   - `repo` (Full control of private repositories) - OR for public repos:
   - `public_repo` (Access public repositories)
5. Click "Generate token"
6. Copy the token immediately (you won't be able to see it again)

### Adding the Token to Repository Secrets (Optional)

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
- Attempt to commit and push the changes automatically

**Note**: If no `SKILL_UPDATE_TOKEN` is configured, the push may fail due to permission restrictions. In this case, you'll need to either:
- Set up the personal access token as described above, OR
- Configure repository settings to allow `GITHUB_TOKEN` to push to the main branch

### Troubleshooting

If the workflow fails with permission errors:
- Verify the `SKILL_UPDATE_TOKEN` secret is set correctly (if using PAT)
- Ensure the token has the required permissions
- Check that the token hasn't expired
- For public repositories, you may need to adjust branch protection rules or repository settings

### Manual Testing

You can trigger the workflow manually from the Actions tab or by dispatching it via the GitHub CLI:

```bash
gh workflow run "Update Skills README"
```