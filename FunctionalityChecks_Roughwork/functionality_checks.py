import subprocess

def run_git(cmd_list, repo_dir):
    proc = subprocess.run(cmd_list, cwd=repo_dir, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr

# Set the path to your local Git repo here
# repo = r"C:\dev\auto-tracker-test"
repo = r"C:/Users/Rakesh-PC/Documents/1_GitHub_Synced/DirSys_autotracking"

# Check git status
print("Initial git status check:--------------")
rc, out = run_git(["git", "status", "--porcelain"], repo)
print(rc, out)

# Stage all changes
print("Staging all changes:--------------")
rc, out = run_git(["git", "add", "-A"], repo)
print(rc, out)
# Check git status
rc, out = run_git(["git", "status", "--porcelain"], repo)
print(rc, out)

# Commit changes
print("Committing changes:--------------")
rc, out = run_git(["git", "commit", "-m", "Auto-commit demo"], repo)
print(rc, out)
# Check git status
rc, out = run_git(["git", "status", "--porcelain"], repo)
print(rc, out)

# Push changes
print("Pushing changes:--------------")
rc, out = run_git(["git", "push"], repo)
print(rc, out)
# Check git status
rc, out = run_git(["git", "status", "--porcelain"], repo)
print(rc, out)

print("Functionality checks completed.")