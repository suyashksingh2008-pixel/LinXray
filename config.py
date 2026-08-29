from pathlib import Path
Evidence_folder=path('evidences')
Report_Folder=path('reports')
Database_file='scan_history.db'
MAX_REDIRECTS=10
MAX_ACTIONS=10
MAX_SCANS_DEPTH=30
SCAN_TIMEOUT=30000
ACTION_WAIT_TIME=1500

ALLOWED_SCHEMES=['http','https']
DANGEROUS_WORDS=[
    'buy','pay','purchase','checkout','delete',
    'remove','submit','confirm','transfer','upload','download','logout','sign out']
Evidence_folder.mkdir(parents=True, exist_ok=True)
Report_Folder.mkdir(parents=True, exist_ok=True)
