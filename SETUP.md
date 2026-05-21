# Fresh Animated Auto-Updating GitHub Profile UI

This package creates a fresh animated SVG profile card for your GitHub profile README.

## Files

```txt
README.md
assets/animated-profile.svg
scripts/generate_animated_profile.py
.github/workflows/update-animated-profile.yml
```

## Upload

1. Upload `README.md`, `assets`, and `scripts` normally.
2. For hidden `.github`, use GitHub web:
   - Add file
   - Create new file
   - Paste this file name exactly:

```txt
.github/workflows/update-animated-profile.yml
```

3. Paste the workflow code from this package and commit.

## Required GitHub setting

Go to:

```txt
Settings → Actions → General → Workflow permissions
```

Select:

```txt
Read and write permissions
```

Save.

## Run it

Go to:

```txt
Actions → Auto Update Animated Profile → Run workflow
```

## Optional profile variables

Add these in:

```txt
Settings → Secrets and variables → Actions → Variables
```

```txt
SOCIAL_INSTAGRAM
SOCIAL_LINKEDIN
SOCIAL_EMAIL
PROFILE_ROLE
PROFILE_TAGLINE
```

Example:

```txt
PROFILE_ROLE = Full-stack Developer · UI/UX Designer · AI Explorer
PROFILE_TAGLINE = Building scalable products at the intersection of code and design.
```

The README stays small. The animated UI lives in `assets/animated-profile.svg` and updates every 6 hours.
