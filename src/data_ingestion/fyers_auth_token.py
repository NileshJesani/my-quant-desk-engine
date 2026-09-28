import argparse
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from fyers_apiv3 import fyersModel
from dotenv import load_dotenv, set_key

# Project root is two levels up from this file:
# src/data_ingestion -> src -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

# ---------- Config from .env ----------
client_id = os.getenv("FYERS_APP_ID")
secret_key = os.getenv("FYERS_SECRET_KEY")
redirect_uri = os.getenv("FYERS_REDIRECT_URI")
auth_code = os.getenv("FYERS_AUTH_CODE")

REQUIRED_FOR_AUTH = {
    "FYERS_APP_ID": client_id,
    "FYERS_SECRET_KEY": secret_key,
    "FYERS_REDIRECT_URI": redirect_uri,
}


def check_required(vars_dict: dict, extra: dict | None = None):
    all_vars = {**vars_dict, **(extra or {})}
    missing = [name for name, value in all_vars.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required Fyers environment variables: " + ", ".join(missing)
        )


# ---------- Fyers session helpers ----------
def make_session(grant_type: str | None = None) -> fyersModel.SessionModel:
    kwargs = dict(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
    )
    if grant_type:
        kwargs["grant_type"] = grant_type
    return fyersModel.SessionModel(**kwargs)


# ---------- Mode: setup auth code ----------
def run_setup(save_token: bool = True):
    check_required(REQUIRED_FOR_AUTH)

    session = make_session()
    auth_url = session.generate_authcode()
    print("Open this URL in your browser and authorize the application:")
    print(auth_url)

    redirected_value = input(
        "Paste the complete redirected URL (or the auth code) here: "
    ).strip()

    if redirected_value.startswith(("http://", "https://")):
        auth_code = parse_qs(urlparse(redirected_value).query).get("auth_code", [""])[0]
    else:
        auth_code = redirected_value

    if not auth_code:
        raise RuntimeError("Could not find auth_code in the redirected URL.")

    set_key(PROJECT_ROOT / ".env", "FYERS_AUTH_CODE", auth_code)
    print("Fyers auth code saved to .env.")

    if save_token:
        print("Now generating access token...")
        run_token(force_auth_code=auth_code)


# ---------- Mode: generate / refresh access token ----------
def run_token(force_auth_code: str | None = None):
    extra_required = {} if force_auth_code else {"FYERS_AUTH_CODE": auth_code}
    check_required(REQUIRED_FOR_AUTH, extra_required)

    used_auth_code = force_auth_code or auth_code

    session = make_session(grant_type="authorization_code")
    session.set_token(used_auth_code)

    response = session.generate_token()
    if response.get("s") == "error" or not response.get("access_token"):
        raise RuntimeError(f"Fyers token generation failed: {response}")

    set_key(PROJECT_ROOT / ".env", "FYERS_ACCESS_TOKEN", response["access_token"])
    print("Fyers access token saved to .env.")


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(
        description="Fyers auth + token helper (single script)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--setup",
        action="store_true",
        help="Run browser-based auth flow, save FYERS_AUTH_CODE (and optionally FYERS_ACCESS_TOKEN).",
    )
    group.add_argument(
        "--token",
        action="store_true",
        help="Use existing FYERS_AUTH_CODE to generate/update FYERS_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--no-auto-token",
        action="store_true",
        help="In --setup mode, do NOT automatically generate the access token afterwards.",
    )

    args = parser.parse_args()

    try:
        if args.setup:
            run_setup(save_token=not args.no_auto_token)
        elif args.token:
            run_token()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()