#!/usr/bin/env python3
import json
import urllib.request
import re
from datetime import datetime

USERNAME = "hardianto01"
README_PATH = "readme.md"

def fetch_events():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=15"
    req = urllib.request.Request(url, headers={"User-Agent": "GitHub-Action-Readme-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def format_event(event):
    etype = event.get("type", "")
    repo_full = event.get("repo", {}).get("name", "")
    repo_name = repo_full.split("/")[-1] if "/" in repo_full else repo_full
    repo_url = f"https://github.com/{repo_full}"
    created = event.get("created_at", "")[:10]
    payload = event.get("payload", {})

    if etype == "PushEvent":
        commits = payload.get("commits", [])
        msg = commits[0].get("message", "commits").split("\n")[0] if commits else "commits"
        if len(msg) > 60:
            msg = msg[:57] + "..."
        return f"- 🚀 Pushed to [`{repo_name}`]({repo_url}): *{msg}* `({created})`"
    elif etype == "CreateEvent":
        ref_type = payload.get("ref_type", "repo")
        return f"- ✨ Created {ref_type} on [`{repo_name}`]({repo_url}) `({created})`"
    elif etype == "WatchEvent":
        return f"- ⭐ Starred [`{repo_name}`]({repo_url}) `({created})`"
    elif etype == "ForkEvent":
        forkee = payload.get("forkee", {}).get("full_name", repo_name)
        return f"- 🍴 Forked [`{repo_name}`]({repo_url}) to `{forkee}` `({created})`"
    elif etype == "ReleaseEvent":
        rel_name = payload.get("release", {}).get("name", "release")
        return f"- 📦 Published release *{rel_name}* on [`{repo_name}`]({repo_url}) `({created})`"
    elif etype == "IssuesEvent":
        action = payload.get("action", "activity")
        title = payload.get("issue", {}).get("title", "")
        return f"- 🐛 {action.capitalize()} issue *{title}* on [`{repo_name}`]({repo_url}) `({created})`"
    return None

def main():
    events = fetch_events()
    lines = []
    seen = set()

    for ev in events:
        formatted = format_event(ev)
        if formatted and formatted not in seen:
            lines.append(formatted)
            seen.add(formatted)
        if len(lines) >= 6:
            break

    if not lines:
        print("No events formatted. Keeping existing readme.")
        return

    content_to_insert = "\n".join(lines)
    print(f"Generated activities:\n{content_to_insert}")

    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme = f.read()

        start_tag = "<!-- RECENT_ACTIVITY:START -->"
        end_tag = "<!-- RECENT_ACTIVITY:END -->"

        pattern = re.compile(rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
        replacement = f"{start_tag}\n{content_to_insert}\n{end_tag}"

        if start_tag in readme and end_tag in readme:
            new_readme = pattern.sub(replacement, readme)
            with open(README_PATH, "w", encoding="utf-8") as f:
                f.write(new_readme)
            print("Successfully updated readme.md!")
        else:
            print("Tags not found in readme.md.")
    except Exception as e:
        print(f"Error updating readme: {e}")

if __name__ == "__main__":
    main()
