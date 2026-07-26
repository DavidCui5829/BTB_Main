"""Invoke Descript's Agent to turn each uploaded clip into an engaging short."""

import json
import os
import sys
import time

import requests

TOKEN = os.environ.get("DESCRIPT_TOKEN", "")
BASE = "https://descriptapi.com/v1"
HEAD = {"Authorization": f"Bearer {TOKEN}"}

PROJECT_ID = "e4f5cec9-b9e4-4845-9a20-dd9569a2b9c2"

COMPOSITIONS = {
    "01_how_i_got_into_nasa": "fe17b708-e20b-4916-9041-a4cbcd719a5d",
    "02_astronaut_almost_drowned": "89b6fbc2-1f05-4e2b-8def-d9abd7d1133a",
    "03_training_in_giant_pool": "f00527ea-ac3a-4f46-97d4-534d88efa905",
    "04_smallest_hazards_most_dangerous": "991e86fe-4bac-4e02-918d-b6f9b37f634e",
    "05_best_time_space_industry": "325ed4f9-8292-4bff-a833-ebdf852273fe",
}

PROMPT = (
    "Turn this clip into an engaging social-media short. Remove filler words "
    "(um, uh, like, you know) and long silences, tighten it to the single most "
    "compelling moment, and add bold animated captions. Make it punchy and "
    "ready to post."
)


def poll(job_id, tries=50, delay=8):
    for i in range(tries):
        r = requests.get(f"{BASE}/jobs/{job_id}", headers=HEAD)
        data = r.json()
        state = data.get("job_state") or data.get("state")
        print(f"    poll {i+1}: {state}")
        if state in ("stopped", "complete", "completed", "succeeded", "failed", "error"):
            return data
        time.sleep(delay)
    return {}


def run(name, comp_id):
    body = {"project_id": PROJECT_ID, "composition_id": comp_id, "prompt": PROMPT}
    r = requests.post(f"{BASE}/jobs/agent", headers=HEAD, json=body)
    print(f"[{name}] agent POST HTTP {r.status_code}")
    if r.status_code >= 300:
        print(r.text[:1500])
        return None
    job_id = r.json().get("job_id")
    print(f"    job_id={job_id}, model={r.json().get('resolved_model')}")
    result = poll(job_id)
    res = result.get("result", {})
    print(f"    project_changed={res.get('project_changed')} credits={res.get('ai_credits_used')}")
    print(f"    agent_response: {str(res.get('agent_response'))[:600]}")
    return result


def main():
    if not TOKEN:
        print("Set DESCRIPT_TOKEN")
        sys.exit(1)
    targets = sys.argv[1:] or list(COMPOSITIONS)
    out = {}
    for name in targets:
        cid = COMPOSITIONS.get(name)
        if not cid:
            print(f"[skip] unknown composition {name}")
            continue
        out[name] = run(name, cid)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descript_agent_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)


if __name__ == "__main__":
    main()
