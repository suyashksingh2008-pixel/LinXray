import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

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


def run_scan(target_url: str, output_root: Path = Path("evidence_folder")) -> Path:
    target_url = validate_basic_url(target_url)

    scan_id = str(uuid4())

    output_root.mkdir(parents=True, exist_ok=True)
    output_root = output_root.resolve()

    host_evidence_folder = (output_root / scan_id)

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

    actions_path = (host_evidence_folder / "actions_exec.json")

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


def main() -> None:
    test_url = input("Enter the URL to scan: ").strip()

    try:
        evidence_folder = run_scan(test_url, output_root= Path("evidence_folder"))
        print("\nTesting completed successfully")
        print(f"Evidence folder:\n"f"{evidence_folder}")

        print("\nCreated files:")

        for file_path in sorted(evidence_folder.iterdir()):
            print(f"- {file_path.name}")

    except Exception as error:
        print("\nTesting failed")
        print(error)


if __name__ == "__main__":
    main()

    

    
    
        
    
