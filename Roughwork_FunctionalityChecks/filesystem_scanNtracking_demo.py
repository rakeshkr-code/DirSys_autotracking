import os
import json

def scan_dir(root):
    """
    Walk through the directory and collect a snapshot of all files
    (excluding .git folders). Stores file path, mtime, and size.
    """
    snap = {}
    for dirpath, _, filenames in os.walk(root):
        if '.git' in dirpath.split(os.sep):
            continue
        for fname in filenames:
            full = os.path.join(dirpath, fname)
            try:
                st = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, root)
            snap[rel] = [st.st_mtime, st.st_size]
    return snap

def save_state(path, state):
    """
    Save the snapshot (state) to a JSON file.
    Automatically creates the folder if it doesn't exist.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def load_state(path):
    """
    Load the previous snapshot (state) from JSON.
    Returns {} if file is missing or empty/invalid.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def compare_snapshots(old, new):
    """
    Compare previous and current snapshots.
    Returns 3 lists: added, modified, and deleted files.
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    added = list(new_keys - old_keys)
    deleted = list(old_keys - new_keys)

    modified = []
    for key in old_keys & new_keys:
        if old[key] != new[key]:
            modified.append(key)

    return added, modified, deleted

if __name__ == "__main__":
    # 👇👇 CHANGE THIS TO THE DIRECTORY YOU WANT TO TRACK 👇👇
    target_dir = r"C:\Users\Rakesh-PC\Documents\1_GitHub_Synced\DirSys_autotracking\Roughwork_FunctionalityChecks"

    # Location of state file (where snapshot will be saved)
    state_file = os.path.join(target_dir, "state.json")

    # Step 1: Scan current state
    current = scan_dir(target_dir)

    # Step 2: Load previous state
    previous = load_state(state_file)

    # Step 3: Compare current vs previous
    added, modified, deleted = compare_snapshots(previous, current)

    # Step 4: Print changes
    print("📁 Added files:")
    print("\n".join(added) or "  None")

    print("✏️ Modified files:")
    print("\n".join(modified) or "  None")

    print("❌ Deleted files:")
    print("\n".join(deleted) or "  None")

    # Step 5: Save current state for next run
    save_state(state_file, current)
