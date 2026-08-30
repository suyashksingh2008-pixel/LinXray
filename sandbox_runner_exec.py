import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4
from config import DATABASE_FILE
from database import (
    fetch_pending_scan,
    mark_scan_completed,
    mark_scan_failed,
    mark_scan_processing,
)

from validation import (
    safe_username,
    validate_url,
)

DOCKER_IMAGE = "linxray-dispscanner:latest"

SCAN_TIMEOUT_TIME = 360

def validate_basic_url(target_url: str) -> str:
    target_url = target_url.strip()
    parsed_url = urlparse(target_url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")
    if not parsed_url.hostname:
        raise ValueError("The URL does not contain a valid hostname")

    return target_url


def run_scan(target_url: str, username: str, scan_id: str, output_root: Path = Path("evidence_folder")) -> Path:
    target_url = validate_basic_url(target_url)
    username = safe_username(username)

    output_root.mkdir(parents=True, exist_ok=True)
    output_root = output_root.resolve()

    host_evidence_folder = output_root / username
    host_evidence_folder.mkdir(parents=True, exist_ok=True)

    command = ["docker",
            "run",
            "--rm",
    
            
            "--memory",
            "512m",
            "--cpus",
            "1.0",
            "--pids-limit",
            "200",
    
            
            "--cap-drop",
            "ALL",
    
            
            "--security-opt",
            "no-new-privileges",
    
            
            "--read-only",
    
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=256m",

            "--network",
            "bridge",
    
            "--mount",
            (
                f"type=bind,"
                f"source={output_root},"
                f"target=/output"
            ),
    
            DOCKER_IMAGE,
    
            # Arguments received by scanner_entry.py
            "--url",
            target_url,

            "--username",
            username,
    
            "--scan-id",
            scan_id,
    
            "--output",
            "/output"
        ]
    print(f"Created scan id: {scan_id}")
    print("Starting isolated Docker scanner......")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=SCAN_TIMEOUT_TIME)
    except FileNotFoundError as error:
        raise RuntimeError("Docker was not found or is not running") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("The scanner exceeded the allowed runtime of "f"{SCAN_TIMEOUT_TIME} seconds") from error
    except subprocess.CalledProcessError as error:
        error_message = (error.stderr.strip() or error.stdout.strip() or "The Docker scanner failed")
        raise RuntimeError(f"Scanner container error:\n{error_message}") from error
    if result.stdout:
        print(result.stdout.strip())
    if not host_evidence_folder.exists():
        raise RuntimeError("Docker completed, but the evidence folder has not been created")

    screenshots = sorted(host_evidence_folder.glob("*.png"))

    if not screenshots:
        raise RuntimeError("Docker completed, but no screenshots were created")

    actions_path = (host_evidence_folder / f"{scan_id}_actions_exec.json")

    if not actions_path.exists():
        raise RuntimeError("Docker completed, but no actions file was created")
    try:
        actions_data = json.loads(actions_path.read_text(encoding="UTF-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError("The generated JSON file is invalid") from error

    print("Isolated scan completed!")
    print(f"Number of screenshots created: {len(screenshots)}")
    print("Buttons tested: "f"{actions_data.get('buttons_tested',0)}")

    return host_evidence_folder


def main() -> tuple[str, Path] | None:
    scan_request = fetch_pending_scan()

    if scan_request is None:
        print("No pending scan found")
        return None

    username, target_url = scan_request
    scan_id = str(uuid4())

    mark_scan_processing(
        username=username,
        scan_id=scan_id,
    )

    try:
        user_folder = run_scan(
            target_url=target_url,
            username=username,
            scan_id=scan_id,
            output_root=Path("evidence"),
        )

        mark_scan_completed(
            scan_id=scan_id,
            output_folder=str(user_folder),
        )

        print("\nScan completed successfully")
        print(f"Scan ID: {scan_id}")
        print(f"User folder: {user_folder}")

        return scan_id, user_folder

    except Exception as error:
        mark_scan_failed(
            scan_id=scan_id,
            error_message=str(error),
        )

        print("\nScan failed")
        print(error)

        return None


if __name__ == "__main__":
    main()

    

    
    
        
    
