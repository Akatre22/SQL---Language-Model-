"""
Script to fetch and clone curated SQL repositories from GitHub.
Repositories:
1. mouredev/hello-sql
2. civilian7/sql-tutorial
3. DataWithBaraa/sql-ultimate-course
4. datawithdanny/sql-masterclass
5. btholt/complete-intro-to-sql
6. Baeldung/sql-tutorials
7. academind/sql-complete-guide-code
"""

import os
import subprocess
import sys
from pathlib import Path

# Fix windows encoding for stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPOSITORIES = [
    {
        "name": "hello-sql",
        "url": "https://github.com/mouredev/hello-sql.git",
        "desc": "Fundamentals of SQL & relational databases",
    },
    {
        "name": "sql-tutorial",
        "url": "https://github.com/civilian7/sql-tutorial.git",
        "desc": "Realistic e-commerce database with 30 tables & 270 exercises",
    },
    {
        "name": "sql-ultimate-course",
        "url": "https://github.com/DataWithBaraa/sql-ultimate-course.git",
        "desc": "Practical analytical queries, window functions & joins",
    },
    {
        "name": "sql-masterclass",
        "url": "https://github.com/datawithdanny/sql-masterclass.git",
        "desc": "Advanced SQL problem solving and CTEs",
    },
    {
        "name": "complete-intro-to-sql",
        "url": "https://github.com/btholt/complete-intro-to-sql.git",
        "desc": "Relational DB fundamentals, PostgreSQL, joins, indexes",
    },
    {
        "name": "sql-tutorials",
        "url": "https://github.com/Baeldung/sql-tutorials.git",
        "desc": "In-depth SQL guides, recipes, and best practices",
    },
    {
        "name": "sql-complete-guide-code",
        "url": "https://github.com/academind/sql-complete-guide-code.git",
        "desc": "CRUD, relationships, constraints, schemas & views",
    },
]

def fetch_repos(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    # Enable long paths for git on Windows
    try:
        subprocess.run(["git", "config", "--global", "core.longpaths", "true"], check=False)
    except Exception:
        pass
        
    print(f"[*] Target directory for raw repositories: {target_dir.resolve()}")
    
    for repo in REPOSITORIES:
        repo_name = repo["name"]
        repo_url = repo["url"]
        dest_path = target_dir / repo_name
        
        print(f"\n--- Processing: {repo_name} ({repo['desc']}) ---")
        if dest_path.exists() and (dest_path / ".git").exists():
            print(f"[+] '{repo_name}' already exists at {dest_path}. Restoring/Pulling...")
            try:
                subprocess.run(["git", "-C", str(dest_path), "config", "core.longpaths", "true"], check=False)
                subprocess.run(["git", "-C", str(dest_path), "restore", "--source=HEAD", ":/"], check=False)
                subprocess.run(["git", "-C", str(dest_path), "pull"], check=False)
                print(f"[SUCCESS] Updated {repo_name}")
            except Exception as e:
                print(f"[!] Warning updating {repo_name}: {e}")
        else:
            print(f"[+] Cloning {repo_url} (depth=1)...")
            try:
                res = subprocess.run(
                    ["git", "-c", "core.longpaths=true", "clone", "--depth", "1", repo_url, str(dest_path)],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if res.returncode == 0:
                    print(f"[SUCCESS] Successfully cloned {repo_name}")
                else:
                    print(f"[!] Git clone message for {repo_name}: {res.stderr.strip()}")
                    # Attempt restore if checkout failed due to longpaths
                    if dest_path.exists():
                        subprocess.run(["git", "-C", str(dest_path), "config", "core.longpaths", "true"], check=False)
                        subprocess.run(["git", "-C", str(dest_path), "checkout", "-f", "HEAD"], check=False)
            except Exception as e:
                print(f"[!] Exception during cloning {repo_name}: {e}")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    raw_repos_dir = base_dir / "raw_repos"
    fetch_repos(raw_repos_dir)
