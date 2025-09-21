"""
Directory auto-tracker for Windows.
Usage examples:
  python tracker.py --watch-dir "C:\projects\myrepo" --state-file "C:\track\myrepo_state.json" --log-file "C:\track\myrepo_log.txt" --interval 1800 --daemon
  python tracker.py --watch-dir "C:\projects\myrepo" --state-file "C:\track\myrepo_state.json" --log-file "C:\track\myrepo_log.txt" --once
"""
import os
import json
import time
import argparse
import subprocess
from datetime import datetime

def scan_dir(root_dir, exclude_dirs=(".git",)):
    snapshot = {}
    root_dir = os.path.abspath(root_dir)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # skip excluded directories anywhere in path
        if any(excl in dirpath.split(os.sep) for excl in exclude_dirs):
            continue
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            try:
                st = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, root_dir)
            snapshot[rel] = [st.st_mtime, st.st_size]
    return snapshot

def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def append_log(log_file, text):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def run_git_commands(repo_dir, commit_message, log_file):
    def run(cmd):
        proc = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        append_log(log_file, f"[{datetime.now().isoformat()}] CMD: {' '.join(cmd)}")
        append_log(log_file, proc.stdout.strip() or proc.stderr.strip())
        return proc.returncode, proc.stdout + proc.stderr

    # add all
    rc, out = run(["git", "add", "-A"])
    if rc != 0:
        append_log(log_file, f"[{datetime.now().isoformat()}] git add failed: {out}")
        return False

    # commit
    rc, out = run(["git", "commit", "-m", commit_message])
    if rc != 0:
        # if commit failed because nothing to commit (rare since we detected changes), log and continue
        append_log(log_file, f"[{datetime.now().isoformat()}] git commit returned non-zero: {out}")
        return False

    # push
    rc, out = run(["git", "push"])
    if rc != 0:
        append_log(log_file, f"[{datetime.now().isoformat()}] git push failed: {out}")
        return False

    return True

def format_change_summary(added, modified, deleted, max_items=20):
    def list_preview(xs):
        xs = sorted(xs)
        if not xs:
            return "none"
        if len(xs) <= max_items:
            return ", ".join(xs)
        return ", ".join(xs[:max_items]) + f", ...(+{len(xs)-max_items} more)"
    return f"Added: {len(added)} ({list_preview(added)}); Modified: {len(modified)} ({list_preview(modified)}); Deleted: {len(deleted)} ({list_preview(deleted)})"

def check_once(watch_dir, state_file, log_file):
    watch_dir = os.path.abspath(watch_dir)
    if not os.path.isdir(watch_dir):
        raise SystemExit(f"watch-dir does not exist: {watch_dir}")

    old = load_state(state_file)
    new = scan_dir(watch_dir)
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    added = list(new_keys - old_keys)
    deleted = list(old_keys - new_keys)
    modified = [k for k in (new_keys & old_keys) if (old.get(k) != new.get(k))]

    if not (added or deleted or modified):
        append_log(log_file, f"[{datetime.now().isoformat()}] No changes detected in {watch_dir}")
        # still save snapshot (timestamp changed?) - keep previous snapshot to detect real changes
        return False

    summary = format_change_summary(added, modified, deleted)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{ts} | Changes detected in {watch_dir} | {summary}"
    append_log(log_file, entry)
    # build commit message
    details = []
    if added:
        details.append(f"Added: {len(added)}")
    if modified:
        details.append(f"Modified: {len(modified)}")
    if deleted:
        details.append(f"Deleted: {len(deleted)}")
    commit_message = f"Auto-commit: {ts} — {'; '.join(details)}"
    # try git operations
    success = run_git_commands(watch_dir, commit_message, log_file)
    if success:
        append_log(log_file, f"{ts} | Commit & push successful | {summary}")
    else:
        append_log(log_file, f"{ts} | Commit or push failed | {summary}")
    # update saved snapshot only if git commit succeeded or even if not? We'll update anyway to avoid re-reporting same change repeatedly.
    save_state(state_file, new)
    return success

def main():
    parser = argparse.ArgumentParser(description="Directory auto-tracker")
    parser.add_argument("--watch-dir", required=True, help="Folder to track (must be a git repo)")
    parser.add_argument("--state-file", required=True, help="Path to state JSON file (outside watch-dir recommended)")
    parser.add_argument("--log-file", required=True, help="Path to append-only logfile (outside watch-dir recommended)")
    parser.add_argument("--interval", type=int, default=1800, help="Interval seconds between checks when daemonizing (default 1800 = 30 min)")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in a loop")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit (useful for Task Scheduler)")
    args = parser.parse_args()

    if not (args.daemon or args.once):
        # default to one-shot (safe)
        args.once = True

    try:
        if args.daemon:
            append_log(args.log_file, f"[{datetime.now().isoformat()}] Starting daemon mode for {args.watch_dir}, interval {args.interval}s")
            while True:
                try:
                    check_once(args.watch_dir, args.state_file, args.log_file)
                except Exception as e:
                    append_log(args.log_file, f"[{datetime.now().isoformat()}] ERROR during check: {e}")
                time.sleep(args.interval)
        else:
            check_once(args.watch_dir, args.state_file, args.log_file)
    except KeyboardInterrupt:
        append_log(args.log_file, f"[{datetime.now().isoformat()}] Stopped by user")

if __name__ == "__main__":
    main()
