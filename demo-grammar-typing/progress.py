# Tiny local progress store for Grammar Tap. Single profile, no accounts.
#
# Shape:
#   { "units": { "<unit_id>": {"badge": "mastered"|"started",
#                              "weak": [item_index, ...]} } }
# An item is identified by its index within its unit's "items" list.
# Units never seen are simply absent ("untouched").

import json
import os

PATH = os.path.join(os.path.dirname(__file__), "progress.json")


def load():
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, ValueError):
        return {"units": {}}
    if not isinstance(data, dict) or "units" not in data:
        return {"units": {}}
    return data


def save(data):
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PATH)


def badge_for(data, unit_id):
    return data["units"].get(str(unit_id), {}).get("badge", "untouched")


def update_unit(data, unit_id, weak_indices):
    """Record a unit's outcome after a run. Empty weak list => mastered."""
    weak = sorted(set(weak_indices))
    data["units"][str(unit_id)] = {
        "badge": "mastered" if not weak else "started",
        "weak": weak,
    }
