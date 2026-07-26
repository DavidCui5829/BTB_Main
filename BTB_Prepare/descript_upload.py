"""Upload Mutahar's ffmpeg highlight clips to Descript and let the Agent
generate interesting short clips.

Flow (per Descript API docs, base https://descriptapi.com/v1):
  1. POST /jobs/import/project_media  -> signed upload_urls + job_id
  2. PUT each clip's bytes to its signed URL
  3. GET /jobs/{job_id} until finished -> project_id
  4. POST /jobs/agent with a highlight prompt -> agent job_id
"""

import json
import os
import sys
import time

import requests

TOKEN = os.environ.get("DESCRIPT_TOKEN", "")
BASE = "https://descriptapi.com/v1"
HEAD = {"Authorization": f"Bearer {TOKEN}"}

CLIP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MutaharMehkri", "clips")
CLIPS = [
    "01_how_i_got_into_nasa.mp4",
    "02_astronaut_almost_drowned.mp4",
    "03_training_in_giant_pool.mp4",
    "04_smallest_hazards_most_dangerous.mp4",
    "05_best_time_space_industry.mp4",
]
PROJECT_NAME = "Mutahar Mehkri - Interview Highlights"


def pretty(label, resp):
    print(f"--- {label}: HTTP {resp.status_code} ---")
    try:
        print(json.dumps(resp.json(), indent=2)[:2500])
    except Exception:
        print(resp.text[:2000])
    print()


def do_import():
    add_media = {}
    add_comps = []
    for name in CLIPS:
        path = os.path.join(CLIP_DIR, name)
        add_media[name] = {
            "content_type": "video/mp4",
            "file_size": os.path.getsize(path),
        }
        add_comps.append({"name": os.path.splitext(name)[0], "clips": [{"media": name}]})

    body = {
        "project_name": PROJECT_NAME,
        "add_media": add_media,
        "add_compositions": add_comps,
    }
    r = requests.post(f"{BASE}/jobs/import/project_media", headers=HEAD, json=body)
    pretty("import request", r)
    r.raise_for_status()
    return r.json()


def upload_files(import_resp):
    urls = import_resp.get("upload_urls") or import_resp.get("uploadUrls") or {}
    if not urls:
        print("!! no upload_urls in response; keys =", list(import_resp.keys()))
        sys.exit(1)
    for name in CLIPS:
        entry = urls.get(name)
        if not entry:
            print(f"!! no upload url for {name}")
            continue
        url = entry["upload_url"] if isinstance(entry, dict) else entry
        path = os.path.join(CLIP_DIR, name)
        with open(path, "rb") as f:
            put = requests.put(url, data=f, headers={"Content-Type": "application/octet-stream"})
        print(f"PUT {name}: HTTP {put.status_code}")


def poll(job_id, tries=40, delay=6):
    for i in range(tries):
        r = requests.get(f"{BASE}/jobs/{job_id}", headers=HEAD)
        data = r.json()
        state = data.get("job_state") or data.get("state") or data.get("status")
        print(f"  poll {i+1}: state={state}")
        if state in ("stopped", "complete", "completed", "succeeded", "failed", "error"):
            return data
        time.sleep(delay)
    return {}


def main():
    if not TOKEN:
        print("Set DESCRIPT_TOKEN env var")
        sys.exit(1)

    step = sys.argv[1] if len(sys.argv) > 1 else "all"

    imp = do_import()
    job_id = imp.get("job_id") or imp.get("jobId")
    upload_files(imp)

    print(f"\nPolling import job {job_id} ...")
    result = poll(job_id)
    print("\n=== import job final ===")
    print(json.dumps(result, indent=2)[:3000])

    with open(os.path.join(os.path.dirname(__file__), "descript_import_result.json"), "w", encoding="utf-8") as f:
        json.dump({"import_request": imp, "job_result": result}, f, indent=2)


if __name__ == "__main__":
    main()
