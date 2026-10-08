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

def fetch_featured_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "GitHub-Action-Readme-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
            filtered = [
                r for r in repos 
                if not r.get("fork") 
                and r.get("name") != USERNAME 
                and r.get("name") != "lontara-lang"
                and r.get("name") != "hardiantojek93"
                and r.get("name") != "assets"
                and not r.get("name").endswith("-template")
            ]
            # Prioritize flagship projects & stars first, then most recently active
            filtered.sort(key=lambda x: (
                x.get("name") == "cctv-gwej",
                x.get("stargazers_count", 0),
                bool(x.get("description")),
                x.get("pushed_at", "")
            ), reverse=True)
            filtered = filtered[:4]

            if not filtered:
                return ""

            lines = []
            for i in range(0, len(filtered), 2):
                chunk = filtered[i:i+2]
                pins = "".join([
                    f'  <a href="{r["html_url"]}"><img src="https://github-readme-stats.vercel.app/api/pin/?username={USERNAME}&repo={r["name"]}&theme=tokyonight&hide_border=true" alt="{r["name"]}" /></a>\n'
                    for r in chunk
                ])
                lines.append(f'<p align="center">\n{pins.rstrip()}\n</p>')
            return "\n".join(lines)
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return ""

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

    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme = f.read()

        # Update Recent Activity
        if lines:
            content_activity = "\n".join(lines)
            start_tag = "<!-- RECENT_ACTIVITY:START -->"
            end_tag = "<!-- RECENT_ACTIVITY:END -->"
            pattern = re.compile(rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
            replacement = f"{start_tag}\n{content_activity}\n{end_tag}"
            if start_tag in readme and end_tag in readme:
                readme = pattern.sub(replacement, readme)
                print("Updated activity section.")

        # Update Featured Projects dynamically
        featured_html = fetch_featured_repos()
        if featured_html:
            feat_start = "<!-- FEATURED_PROJECTS:START -->"
            feat_end = "<!-- FEATURED_PROJECTS:END -->"
            feat_pattern = re.compile(rf"{re.escape(feat_start)}.*?{re.escape(feat_end)}", re.DOTALL)
            feat_replacement = f"{feat_start}\n{featured_html}\n{feat_end}"
            if feat_start in readme and feat_end in readme:
                readme = feat_pattern.sub(feat_replacement, readme)
                print("Updated featured projects section dynamically.")

        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(readme)
        print("Successfully written changes to readme.md!")

    except Exception as e:
        print(f"Error updating readme: {e}")

if __name__ == "__main__":
    main()
