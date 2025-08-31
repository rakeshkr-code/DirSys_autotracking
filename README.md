# Directory System Auto-tracking
Automated Directory and File System Tracking logging, making database etc

## Plan
- stage - 1
    - there will be one specific folder which will be set to track all the time by some s/w code
    - may be in each half an hour it will check for any chenges
    - if there are changes, it will record that with timestamp in a logfile (this will be outside of the folder) and it should auto add, commit with timestamp in the commit msg and push to github, so the logfile will not be tracked by git
    