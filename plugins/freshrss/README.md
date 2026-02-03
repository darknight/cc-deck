# FreshRSS Plugin

FreshRSS reading assistant for Claude Code - fetch, analyze and manage RSS subscription articles.

## Features

- Get unread articles from your FreshRSS instance
- Fetch full article content (static and dynamic rendering)
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
| `article` | Get single article by ID |
| `fetch` | Fetch full content from URL |
| `read` | Mark articles as read |
| `subs` | List subscriptions |

## Requirements

- Python 3.10+
- FreshRSS instance with Google Reader API enabled
- For dynamic content fetching: Playwright with Chromium
