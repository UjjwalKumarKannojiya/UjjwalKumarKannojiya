# Setup

Upload these files/folders to your profile repository:

```text
README.md
assets/profile-card.svg
scripts/generate_profile_svg.py
.github/workflows/update-profile-ui.yml
```

Your profile repo must be public and named exactly like your GitHub username.

## Enable automatic commits

Go to:

```text
Repository → Settings → Actions → General → Workflow permissions
```

Select:

```text
Read and write permissions
```

Then run:

```text
Actions → Auto Update Profile UI → Run workflow
```

## Optional social buttons without hardcoding them in README

Go to:

```text
Repository → Settings → Secrets and variables → Actions → Variables → New repository variable
```

Add any of these:

```text
SOCIAL_INSTAGRAM = https://instagram.com/your_username
SOCIAL_LINKEDIN  = https://www.linkedin.com/in/your-profile/
SOCIAL_EMAIL     = yourmail@gmail.com
```

These are not hardcoded inside README. The workflow reads them and regenerates the SVG.

## How it auto-updates

- Every 6 hours by schedule
- Manually from GitHub Actions
- When you edit the script/workflow/README

The card updates from your GitHub user profile, public repositories, languages, topics, commits, stars, forks, and recent public activity.
