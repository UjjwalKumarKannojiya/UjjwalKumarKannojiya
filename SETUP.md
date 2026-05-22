# Fresh Profile Setup

First delete old profile experiment files if present:
- assets/animated-profile.svg
- assets/profile-card.svg
- assets/hero.svg
- old scripts
- old workflows

Upload:
README.md
profile_config.json
assets/profile-hero.svg
scripts/update_profile.py

For hidden workflow folder, create this file manually on GitHub:
.github/workflows/update-profile.yml

Paste the content from:
WORKFLOW_CODE_COPY_PASTE.txt

Enable:
Settings -> Actions -> General -> Workflow permissions -> Read and write permissions

Run:
Actions -> Update Profile -> Run workflow
