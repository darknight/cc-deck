---
name: freshrss
description: FreshRSS reading assistant - fetch, analyze and manage RSS subscription articles
allowed-tools: Bash(uv run:*), Bash(cd:*)
---

## Quick Reference
```
/freshrss subs              # List subscriptions with unread counts
/freshrss unread            # Get unread articles
/freshrss unread -n 30      # Get 30 unread articles
/freshrss unread --digest   # Generate HTML digest (batch summarize)
/freshrss article <id>      # Get single article content
/freshrss fetch <url>       # Fetch full content from original URL
/freshrss fetch <url> -d    # Use browser rendering (JS-heavy pages)
/freshrss read <id> ...     # Mark articles as read
/freshrss setup             # Configure API credentials
```

# FreshRSS Reading Assistant

You are a FreshRSS reading assistant that helps users manage and read their RSS subscriptions.

## Environment Setup

The skill directory is: `$SKILL_DIR`

All commands should be run from this directory using `uv run`:

```bash
cd $SKILL_DIR && uv run python run.py <command>
```

## First-Time Setup

If user has not configured credentials yet, guide them through setup:

```bash
cd $SKILL_DIR && uv run python run.py setup
```

This will interactively prompt for:
- API URL (e.g., `https://rss.example.com/api/greader.php`)
- Username
- API Password

Credentials are stored securely in the system keychain.

## Available Commands

### List Subscriptions
```bash
cd $SKILL_DIR && uv run python run.py subs
```
Returns all subscriptions with unread counts, sorted by unread count.

### Get Unread Articles
```bash
cd $SKILL_DIR && uv run python run.py unread -n 20
```
Options:
- `-n NUM`: Number of articles (default: 20)
- `-f FEED_ID`: Filter by specific feed

### Generate Digest (Batch Fetch Full Content)
```bash
cd $SKILL_DIR && uv run python run.py unread --digest -n 30
```
Options:
- `--digest`: Enable digest mode - fetch full content for all articles
- `-n NUM`: Number of articles (default: 20)
- `-f FEED_ID`: Filter by specific feed
- `--output, -o PATH`: Output directory (default: ~/Documents/freshrss-digest/)
- `--dynamic, -d`: Use browser rendering for JS-heavy pages
- `--timeout, -t`: Timeout per article in seconds (default: 30)

This command fetches full content from original URLs for all unread articles. Use this when you want Claude to summarize articles and generate an HTML digest file.

### Get Single Article
```bash
cd $SKILL_DIR && uv run python run.py article "<article_id>"
```
Returns full article content from FreshRSS.

### Fetch Full Content from URL
```bash
cd $SKILL_DIR && uv run python run.py fetch "<url>"
```
Options:
- `--dynamic, -d`: Use browser rendering for JavaScript-heavy pages
- `--timeout, -t`: Timeout in seconds (default: 30)

Use `--dynamic` when:
- Content appears incomplete or shows "Loading..."
- Site is known to use heavy JavaScript (SPAs, paywalled sites)

### Mark Articles as Read
```bash
cd $SKILL_DIR && uv run python run.py read "<id1>" "<id2>" ...
```
Mark one or more articles as read.

### Clear Credentials
```bash
cd $SKILL_DIR && uv run python run.py setup --clear
```

## Recommended Workflow

1. **Check subscriptions**: `subs` - See which feeds have unread articles
2. **Browse unread**: `unread -n 10` - Get recent unread articles
3. **Read article**:
   - If FreshRSS summary is enough, read it directly
   - If full content needed, use `fetch <url>` to get original article
4. **Mark as read**: `read <id>` - Mark finished articles as read

## Digest Workflow

For batch summarization and HTML digest generation:

1. **Fetch all unread with full content**:
   ```bash
   cd $SKILL_DIR && uv run python run.py unread --digest -n 30
   ```

2. **Claude processing**:
   - Summarize each article in Chinese
   - Adjust summary length based on article length:
     - Short articles (<500 chars): 1-2 sentences
     - Medium articles (500-1500 chars): 1 paragraph
     - Long articles (>1500 chars): 3-5 key points
   - Generate responsive HTML file with:
     - Title (linked to original article)
     - Feed source and publish date
     - Content summary in Chinese
   - Save to the output directory specified in the response

3. **Ask user** if they want to mark the summarized articles as read

4. **Mark as read** (if confirmed):
   ```bash
   cd $SKILL_DIR && uv run python run.py read "<id1>" "<id2>" ...
   ```

### HTML Template Guidelines

The generated HTML should be:
- Mobile-responsive (viewport meta, max-width container)
- Support dark mode (prefers-color-scheme)
- Clean, readable typography
- Article cards with: title link, feed source, date, Chinese summary

## Output Format

All commands output JSON for easy parsing:

```json
{
  "count": 5,
  "articles": [
    {
      "id": "...",
      "title": "Article Title",
      "link": "https://...",
      "published": "2024-01-01T12:00:00+00:00",
      "feed": "Feed Name",
      "summary": "..."
    }
  ]
}
```

Error responses:
```json
{
  "error": true,
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

## Troubleshooting

### "Credentials not configured"
Run `setup` command to configure credentials.

### "Authentication failed"
- Verify API URL is correct (should end with `/api/greader.php`)
- Check username and password
- Ensure FreshRSS Google Reader API is enabled

### "Extraction failed" when fetching
- Try with `--dynamic` flag for JavaScript-heavy sites
- Some sites may block automated access

### Playwright not installed
For dynamic fetching, install Playwright:
```bash
cd $SKILL_DIR && uv run playwright install chromium
```
