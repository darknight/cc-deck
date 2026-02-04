# FreshRSS Plugin

FreshRSS reading assistant for Claude Code - fetch, analyze and manage RSS subscription articles.

## Features

- Get unread articles from your FreshRSS instance
- Fetch full article content (static and dynamic rendering)
- **Digest mode**: Batch fetch articles for Claude to summarize and generate HTML digest
- Mark articles as read
- List subscriptions with unread counts

## Setup

1. Install the plugin in Claude Code
2. Run `/freshrss` skill
3. Follow the setup instructions to configure credentials

## Credentials

Credentials are securely stored in your system keychain:
- **macOS**: Uses `security` command (Keychain)
- **Linux**: Uses `secret-tool` (libsecret)

## Commands

| Command | Description |
|---------|-------------|
| `setup` | Configure credentials to Keychain |
| `unread` | Get unread articles |
| `unread --digest` | Batch fetch full content for digest generation |
| `article` | Get single article by ID |
| `fetch` | Fetch full content from URL |
| `read` | Mark articles as read |
| `subs` | List subscriptions |

## Digest Workflow

Generate a summarized HTML digest of unread articles:

1. Run `/freshrss unread --digest -n 30` to fetch full content
2. Claude summarizes each article in Chinese
3. Claude generates a responsive HTML file saved to `~/Documents/freshrss-digest/`
4. Optionally mark articles as read

Options for digest mode:
- `-n NUM`: Number of articles (default: 20)
- `--output, -o PATH`: Custom output directory
- `--dynamic, -d`: Use browser rendering for JS-heavy pages
- `--timeout, -t`: Timeout per article in seconds (default: 30)

## Requirements

- Python 3.10+
- FreshRSS instance with Google Reader API enabled
- For dynamic content fetching: Playwright with Chromium
