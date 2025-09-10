import os, json
def scan_dir(root):
    snap = {}
    for dirpath, _, filenames in os.walk(root):
        # skip .git
        if '.git' in dirpath:#.split(os.sep): 
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

if __name__ == "__main__":
    s = scan_dir(r"C:/Users/Rakesh-PC\Documents/1_GitHub_Synced/DirSys_autotracking/")
    print(json.dumps(s, indent=2))
