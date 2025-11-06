[README.md](https://github.com/user-attachments/files/23383177/README.md)
# African Mining Headlines - Updates

This small project fetches mining headlines from **Mining.com** and filters for **Africa** and **South Africa**. It builds a static `index.html` and (optionally) sends a daily email digest of the top 5 headlines.

**Live site URL** (when deployed to GitHub Pages):
https://bonanggodwin-debug.github.io/african-mining-headlines

## What is included
- `generate_site.py` - Python script that fetches the RSS feed, filters for keywords, creates `index.html`, and sends a daily email via SendGrid.
- `.github/workflows/update.yml` - GitHub Action that runs daily and triggers the script.
- This README with setup instructions.

## Quick setup (GitHub web, no local installs required)
1. Create a new GitHub repository named `african-mining-headlines` (or use this repo).
2. Upload the files from this ZIP (or drag & drop the files into the repo via the web UI).
3. In the repo → **Settings → Pages**, enable GitHub Pages (Branch: `main`, Folder: `/ (root)`).
4. Add the following **Repository secrets** (go to Settings → Secrets → Actions):
   - `SENDGRID_API_KEY` - your SendGrid API key (create a free SendGrid account at https://sendgrid.com)
   - `RECIPIENT_EMAIL` - your email address (e.g., `bonanggodwin@gmail.com`)
   - `SENDER_EMAIL` - (optional) the "from" email address; default is `no-reply@african-mining-headlines.example`

> Note: Do **not** commit your API keys into the repository. Use GitHub Secrets as shown above.

## How it works
- The GitHub Action runs daily (05:00 UTC) and also supports manual runs from the Actions tab.
- It installs dependencies, runs `generate_site.py`, writes `index.html` and attempts to send an email with the top 5 headlines using SendGrid.
- If `RECIPIENT_EMAIL` or `SENDGRID_API_KEY` are not set, the site will still be generated but email sending will be skipped.

## Customize
- Change keywords in `generate_site.py` by editing the `KEYWORDS` list.
- Change how many items are included in the email by modifying `MAX_EMAIL_ITEMS` in `generate_site.py`.

## Troubleshooting
- Check the **Actions** tab to see workflow runs and logs.
- If email sending fails, verify your SendGrid API key and that your SendGrid account is allowed to send to your recipient address (some new accounts require verification).

---
Site title: **African Mining Headlines - Updates**
Email subject: **Your Daily Mining News Summary**
