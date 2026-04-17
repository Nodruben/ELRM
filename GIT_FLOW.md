# Simplified Git Flow Guidelines

This repository follows a simplified version of the Git Flow branching strategy. This ensures a clean and organized history while allowing for parallel development.

## Branch Structure

### 1. `main` branch
* **Purpose:** The `main` branch is the primary branch for production-ready code. It reflects the exact state of the currently deployed application.
* **Rules:**
  * Direct commits to `main` are strictly forbidden.
  * All code must be merged into `main` via a Pull Request (PR).
  * Merges into `main` should ideally come from the `develop` branch (for regular releases) or `hotfix/*` branches (for urgent fixes).
  * Every merge into `main` should be tagged with a new version number.

### 2. `develop` branch
* **Purpose:** The `develop` branch is the integration branch for all new features. It serves as the staging area for the next release.
* **Rules:**
  * All feature branches branch off from `develop`.
  * All feature branches are merged back into `develop` via a PR.
  * When `develop` reaches a stable state and is ready for release, it is merged into `main`.

### 3. `feature/*` branches
* **Purpose:** Used to develop new features or non-urgent bug fixes.
* **Naming Convention:** `feature/<issue-number>-<short-description>` or `feature/<short-description>` (e.g., `feature/add-redis-cache`, `feature/123-user-login`).
* **Rules:**
  * Created from: `develop`
  * Merged back into: `develop`
  * Once the feature is complete and tested, open a PR against `develop`.

### 4. `hotfix/*` branches (Optional but recommended)
* **Purpose:** Used for urgent bug fixes in production that cannot wait for the next regular release.
* **Naming Convention:** `hotfix/<short-description>` (e.g., `hotfix/fix-payment-crash`).
* **Rules:**
  * Created from: `main`
  * Merged back into: `main` AND `develop` (to ensure the fix is not lost in future releases).
  * Open PRs against both `main` and `develop` when the fix is complete.

## Workflow Summary

1. **Start a new feature:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/my-new-feature
   ```

2. **Work on your feature:**
   Make changes, commit, and push to your remote branch:
   ```bash
   git add .
   git commit -m "feat: implement my new feature"
   git push origin feature/my-new-feature
   ```

3. **Complete the feature:**
   Open a Pull Request on GitHub from `feature/my-new-feature` targeting the `develop` branch.

4. **Release:**
   When `develop` is ready for production, open a Pull Request from `develop` targeting the `main` branch.

5. **Hotfixes (Emergency):**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-bug
   # Fix the bug, commit, and push
   git push origin hotfix/critical-bug
   ```
   Open a PR to `main` and another PR to `develop`.
