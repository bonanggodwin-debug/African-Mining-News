#!/usr/bin/env python3
import feedparser
from datetime import datetime
import os
import html
import traceback

# Configuration
FEED_URL = "https://www.mining.com/feed/"
KEYWORDS = ["africa", "south africa"]
SITE_TITLE = "African Mining Headlines - Updates"
MAX_EMAIL_ITEMS = 5

# SendGrid settings (read from environment variables)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # e.g. "you@example.com"
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@african-mining-headlines.example")

def matches_keywords(text):
    if not text:
        return False
    t = text.lower()
    return any(k in t for k in KEYWORDS)

def build_index_html(items):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    html_parts = [f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<title>{SITE_TITLE}</title>
<style>
body { font-family: Arial, sans-serif; background:#fafafa; color:#222; padding:2rem; }
.container { max-width:900px; margin:0 auto; }
h1 { color:#2c3e50; }
.article { background: #fff; padding:1rem; margin-bottom:1rem; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.08); }
a { color:#0066cc; text-decoration:none; }
a:hover { text-decoration:underline; }
.meta { color:#666; font-size:0.9rem; }
.summary { margin-top:0.5rem; color:#333; }
footer { margin-top:2rem; color:#777; font-size:0.9rem; }
</style>
</head>
<body>
<div class=\"container\">
<h1>{SITE_TITLE}</h1>
<p>Updated: {timestamp}</p>
"""]

    if not items:
        html_parts.append("<p>No recent Africa-related mining headlines found.</p>")

    for it in items:
        title = html.escape(it.get('title', 'No title'))
        link = html.escape(it.get('link', '#'))
        summary = html.escape(it.get('summary', ''))
        published = html.escape(it.get('published', ''))
        html_parts.append('''
\n<div class="article">
  <h2><a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a></h2>
  <div class="meta">{published}</div>
  <div class="summary">{summary}</div>
</div>\n'''.format(title=title, link=link, summary=summary, published=published))

    html_parts.append('\n<footer>Source: <a href="https://www.mining.com" target="_blank" rel="noopener noreferrer">Mining.com</a></footer>\n</div>\n</body>\n</html>')
    return "".join(html_parts)

def make_email_content(items):
    top = items[:MAX_EMAIL_ITEMS]
    subject = "Your Daily Mining News Summary"
    plain_lines = [subject, '', 'Top headlines:']
    html_lines = ['<h2>' + subject + '</h2>', '<ol>']
    for it in top:
        title = it.get('title', 'No title')
        link = it.get('link', '#')
        summary = it.get('summary', '')
        published = it.get('published', '')
        plain_lines.append(f"- {title} ({published})\n  {link}\n  {summary}\n")
        html_lines.append('<li><a href="' + html.escape(link) + '">' + html.escape(title) + '</a><br/><small>' + html.escape(published) + '</small><p>' + html.escape(summary) + '</p></li>')

    html_lines.append('</ol>')
    html_body = '\n'.join(html_lines)
    plain_body = '\n'.join(plain_lines)
    return subject, plain_body, html_body

def send_email_via_sendgrid(subject, plain_body, html_body):
    if not SENDGRID_API_KEY or not RECIPIENT_EMAIL:
        print('SendGrid API key or recipient email not configured. Skipping email send.')
        return False, 'Missing configuration'

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
    except Exception as e:
        print('SendGrid library not installed. Install "sendgrid" package in your environment.')
        return False, str(e)

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=RECIPIENT_EMAIL,
        subject=subject,
        plain_text_content=plain_body,
        html_content=html_body
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        resp = sg.send(message)
        print('Email send response:', resp.status_code)
        return True, f'Sent ({resp.status_code})'
    except Exception as e:
        print('Error sending email:', e)
        traceback.print_exc()
        return False, str(e)

def main():
    print('Parsing feed:', FEED_URL)
    feed = feedparser.parse(FEED_URL)
    entries = []
    for entry in feed.entries:
        title = entry.get('title', '')
        summary = entry.get('summary', '') or entry.get('description', '')
        link = entry.get('link', '')
        published = entry.get('published', '') or entry.get('updated', '')
        if matches_keywords(title) or matches_keywords(summary):
            entries.append({
                'title': title,
                'summary': summary,
                'link': link,
                'published': published
            })

    try:
        entries_sorted = sorted(entries, key=lambda e: e.get('published', ''), reverse=True)
    except Exception:
        entries_sorted = entries

    index_html = build_index_html(entries_sorted)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    print('Wrote index.html with', len(entries_sorted), 'items.')

    subject, plain_body, html_body = make_email_content(entries_sorted)
    sent, info = send_email_via_sendgrid(subject, plain_body, html_body)
    print('Email status:', sent, info)

if __name__ == '__main__':
    main()