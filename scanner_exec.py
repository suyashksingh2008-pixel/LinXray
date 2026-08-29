import json
import re
from pathlib import Path
from typing import Optional
import argparse

from playwright.sync_api import(Browser, BrowserContext, Locator, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright)

PAGE_TIMEOUT_MS = 30_000
CLICK_TIMEOUT_MS = 5_000
AFTER_CLICK_WAIT_MS = 2_000
MAX_BUTTONS_TO_CLICK = 10
SCREENSHOT_TIMEOUT_MS = 30_000

BUTTON_SELECTOR = "button, input[type='button], [role='button], a[href]"
EXAMINE_BUTTON_PHRASES = {
    "contact us",
    "view product",
    "pay",
    "payment",
    "purchase",
    "buy",
    "order",
    "checkout",
    "subscribe",
    "donate",
    "transfer",
    "send money",

    "submit",
    "send",
    "confirm",
    "verify",
    "login",
    "log in",
    "sign in",
    "sign up",
    "register",}

BLOCKED_BUTTON_PHRASES = {

    "delete",
    "remove",
    "erase",
    "logout",
    "log out",

    "download",
    "install",
    "upload",
    "choose file",

    "allow",
    "enable",
    "grant access",
    "camera",
    "microphone",
    "location",

    "accept offer",
    "claim",
    "redeem",
    "continue",
    "proceed",
    "next"
}

def clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", "", text).strip().lower()

def safe_filename(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return cleaned[:40] or "unnamed button"

def get_button_label(button: Locator) -> str:
    candidates = []

    try:
        candidates.append(button.inner_text(timeout=1_000))
    except Exception:
        pass

    for attribute in ["value", "aria-label", "title", "name"]:
        try:
            candidates.append(button.get_attribute(attribute))
        except Exception:
            pass
    for candidate in candidates:
        if candidate and candidate.strip():
            return candidate.strip()
    return "Unnamed button"

def get_button_type(button: Locator) -> tuple[bool, str, str]:
    try:
        button_type = button.get_attribute("type")
    except Exception:
        button_type = None

    return clean_text(button_type)

def classify_button(button: Locator) -> tuple[bool, str, str]:
    label = get_button_label(button)
    cleaned_label = clean_text(label)
    button_type = get_button_type(button)

    if not cleaned_label:
        return False, label, "Button has no readable label"
    if button_type in {"submit", "reset"}:
        return (False, label, f"Blocked button tyoe: {button_type}")
    try:
        href = button.get_attribute("href")
    except Exception:
        href = None
    if href:
        cleaned_href = href.strip().lower()
    if cleaned_href.startswith(("mailto:", "tel:", "javascript:")):
        return (False, label, "Blocked non-web link")
    if any(phrase in cleaned_label for phrase in BLOCKED_BUTTON_PHRASES):
        return (False, label, "Label contains a blocked action")
    if any(phrase in cleaned_label for phrase in BLOCKED_BUTTON_PHRASES):
            return (False, label, "Label is not in the informational allow-list")

    return (True, label, "Label has informational action")

def configure_context(browser: Browser) -> BrowserContext:
    context = browser.new_context(viewport={"width": 1440, "height": 900}, ignore_https_errors=False, accept_downloads=False)
    return context

def prepare_page(page: Page) -> None:
    page.set_default_timeout(CLICK_TIMEOUT_MS)
    page.on("dialog", lambda dialog: dialog.dismiss())
    page.on("download",lambda download: download.cancel())

def block_state_changing_requests(context: BrowserContext) -> None:
    def handle_route(route):
        method = route.request.method.upper()

        if method in {"GET", "HEAD", "OPTIONS"}:
            route.continue_()
        else:
            route.abort()
    context.route("**/*", handle_route)

def capture_screenshot(page: Page, screenshot_path: Path) -> None:
    page.wait_for_timeout(3000)

    try:
        page.screenshot(path=str(screenshot_path), full_page=True, timeout=SCREENSHOT_TIMEOUT_MS, animations="disabled", caret="hide")
    except PlaywrightTimeoutError:
        print("Full-page screenshot timed-out.\nCapturing the visible area ahead......")
        page.screenshot(path=str(screenshot_path), full_page=False, timeout=SCREENSHOT_TIMEOUT_MS, animations="disabled", caret="hide")

def collect_button_candidates(page: Page) -> list[dict]:
    clickables = page.locator(BUTTON_SELECTOR)
    clickable_count = clickables.count()

    candidates = []

    for index in range(clickable_count):
        element = clickables.nth(index)

        try:
            if not element.is_visible():
                continue
            if not element.is_enabled():
                continue
            permitted, label, reason = (classify_button(element))
            print(f"Found: {label!r}")
            print(f"Permitted: {permitted}")
            print(f"Reason: {reason}")

            candidates.append({"original_index": index, "label": label, "permitted": permitted, "reason": reason})

        except Exception as error:
            candidates.append({"original_index": index, "label": label, "permitted": False, "reason": str(error)})

    return candidates

def test_button(browser: Browser, target_url: str, button_information: dict, action_number: int, evidence_folder: Path) -> dict:
    context = configure_context(browser)
    page = context.new_page()
    prepare_page(page)

    label = button_information["label"]
    original_index = button_information["original_index"]

    filename_label = safe_filename(label)

    before_name = (f"action_{action_number:02d}_"f"{filename_label}_before.jpeg")
    after_name = (f"action_{action_number:02d}_"f"{filename_label}_after.jpeg")

    before_path = evidence_folder / before_name
    after_path = evidence_folder / after_name

    action_result = {"action_number": action_number, "button_label": label, "status": "failed", "url_before": None, "url_after": None, "before_screenshot": before_name, "after_screenshot": None, "error": None}

    try:
        page.goto(target_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        page.wait_for_timeout(1_500)

        buttons = page.locator(BUTTON_SELECTOR)

        if original_index >= buttons.count():
            raise RuntimeError("Button was not found on the fresh page")

        button = buttons.nth(original_index)

        if not button.is_visible():
            raise RuntimeError("Button is no longer visible")
        if not button.is_enabled():
            raise RuntimeError("Button is no longer enabled")

        permitted, fresh_label, reason = classify_button(button)

        if not permitted:
            raise RuntimeError(f"Button failed second safety check: {reason}")

        action_result["button_label"] = fresh_label
        action_result["url_before"] = page.url

        capture_screenshot(page, before_path)

        block_state_changing_requests(context)

        pages_before_click = len(context.pages)

        button.scroll_into_view_if_needed()
        button.click(timeout=CLICK_TIMEOUT_MS, no_wait_after=True)

        page.wait_for_timeout(AFTER_CLICK_WAIT_MS)

        if len(context.pages) > pages_before_click:
            result_page = context.pages[-1]
            prepare_page(result_page)

            try:
                result_page.wait_for_load_state("domcontentloaded", timeout=5_000)
            except PlaywrightTimeoutError:
                pass
        else:
            result_page = page
        capture_screenshot(result_page, after_path)

        action_result["status"] = "completed"
        action_result["url_after"] = result_page.url
        action_result["after_screenshot"] = after_name

    except Exception as error:
        action_result["error"] = str(error)

        try:
            error_name = (f"action_{action_number:02d}_"f"{filename_label}_error.png")
            capture_screenshot(page, evidence_folder / error_name)
            action_result["error_screenshot"] = (error_name)

        except Exception:
            pass
    finally:
        context.close()

    return action_result

def scan_website(target_url: str, scan_id: str, output_root: str) -> Path:
   evidence_folder = output_root / scan_id
   evidence_folder.mkdir(parents=True, exist_ok=True)

   actions = []

   with sync_playwright() as playwright:
       browser = playwright.chromium.launch(headless= True, args=["--disable-dev-shm-usage"])

       initial_context = configure_context(browser)
       initial_page = initial_context.new_page()
       prepare_page(initial_page)

       try:
            initial_page.goto(target_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            initial_page.wait_for_timeout(2_000)

            capture_screenshot(initial_page, evidence_folder / "initial.png")

            button_candidates = collect_button_candidates(initial_page)

       except PlaywrightTimeoutError as error:
           raise RuntimeError("The initial page took too long to load") from error

       finally:
           initial_context.close()

       permitted_buttons = [candidate for candidate in button_candidates if candidate["permitted"]]
       permitted_buttons = permitted_buttons[:MAX_BUTTONS_TO_CLICK]

       for action_number, button_information in enumerate(permitted_buttons, start= 1):
           result = test_button(browser=browser, target_url=target_url, button_information=button_information, action_number=action_number, evidence_folder=evidence_folder)
           actions.append()

       browser.close()

   skipped_buttons = [candidate for candidate in button_candidates if not candidate["permitted"]]

   action_record = {"scan_id": scan_id, "target_url": target_url, "maximum_actions": MAX_BUTTONS_TO_CLICK, "buttons_found": len(button_candidates), "buttons_tested": len(actions), "actions": actions, "skipped_buttons": skipped_buttons}
   actions_record_path = (evidence_folder / "actions_exec.json")
   actions_record_path.write_text(json.dumps(action_record,indent=4), encoding="utf-8")

   return evidence_folder

def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Linxray Isolated Scanner")

    parser.add_argument("--url", required=True, help="URL to investigate")
    parser.add_argument("--scan-id", required=True, help="Unique scan_id for every scan")
    parser.add_argument("--output", required=True, help="Root output directory inside Docker")

    return parser.parse_args

def main() -> None:
    arguments = get_arguments()

    print(f"Starting scan: {arguments.scan_id}")
    print(f"Target URL: {arguments.url}")

    evidence_folder = scan_website(target_url=arguments.url, scan_id=arguments.scan_id, output_root=Path(arguments.output))
    if not evidence_folder.exists():
        raise RuntimeError("Evidence folder is not created by the scanner")
    
    screenshots = sorted(evidence_folder.glob("*.png"))
    if not screenshots():
        raise RuntimeError("Screenshots have not been clicked by the scanner")

    actions_path = (evidence_folder / "actions_exec.json")
    if not actions_path.exists():
        raise RuntimeError("actions_exec.json file has not been formed")

    try:
        actions_data = json.loads(actions_path.read_text(encoding="UTF-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError("actions_exec.json contains invalid JSON") from error

    print("Scan completed successfully")
    print(f"Evidence folder: {evidence_folder}")
    print(f"Screenshots: {len(screenshots)}")
    print(f"Buttons found: {actions_data.get("buttons_found", 0)}")
    print(f"Buttons tested: {actions_data.get("buttons_tested", 0)}")

if __name__ == "__main__":
    main()    
        