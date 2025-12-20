import argparse
import os
from pathlib import Path

from huggingface_hub import HfApi, create_repo, upload_folder

"""
Deploy the Streamlit dashboard folder to a Hugging Face Space.

Usage:
  set HF_TOKEN=hf_...  # or pass --token
  py -m pip install huggingface_hub
  py scripts/deploy_to_hf.py --space <username>/<space_name>

Notes:
- If the Space does not exist, it will be created (type=space, sdk=streamlit).
- This uploads the contents of the current folder (CallCenter-AIAgent) to the Space root.
- Secrets (.env) are NOT uploaded; set them in Space Settings ➜ Repository secrets.
"""

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--space", required=True, help="<username>/<space_name> (e.g., jackie/callcenter-aiaagent)")
    parser.add_argument("--token", default=os.getenv("HF_TOKEN"), help="HF access token (or set HF_TOKEN env var)")
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("HF token not provided. Set HF_TOKEN env var or pass --token.")

    api = HfApi(token=args.token)

    # Create repo if needed
    try:
        create_repo(repo_id=args.space, repo_type="space", space_sdk="gradio", exist_ok=True, token=args.token)
        print(f"✅ Space ensured: https://huggingface.co/spaces/{args.space}")
    except Exception as e:
        raise SystemExit(f"Failed to create/ensure space: {e}")

    # Upload folder contents (app.py, requirements.txt, runtime.txt, README.md, etc.)
    try:
        upload_folder(
            repo_id=args.space,
            repo_type="space",
            folder_path=str(ROOT),
            token=args.token,
            commit_message="Deploy Streamlit dashboard",
        )
        print("✅ Upload completed. Build will start automatically.")
        print(f"🔗 Space: https://huggingface.co/spaces/{args.space}")
    except Exception as e:
        raise SystemExit(f"Upload failed: {e}")


if __name__ == "__main__":
    main()
