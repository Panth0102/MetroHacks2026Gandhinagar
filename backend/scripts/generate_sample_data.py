"""Deterministic SYNTHETIC data generator for Metro Revenue Intelligence.

ALL output is fictional/synthetic demo data. It is NOT official Ahmedabad Metro,
GMRC, AMTS, BRTS, or any real operator data. A fixed seed makes it reproducible.

Run directly to dump JSON into data/sample/ for inspection:
    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
DATASET_LABEL = "SYNTHETIC — fictional demo data, not real operator data"

# (code, name, line, type, daily_scale, exits_known)
STATIONS = [
    ("STN01", "Riverfront Central", "Blue Line", "interchange", 42000, True),
    ("STN02", "Old Town Bazaar", "Blue Line", "underground", 31000, True),
    ("STN03", "Tech Park East", "Red Line", "elevated", 38000, True),
    ("STN04", "University Gate", "Red Line", "elevated", 26000, False),  # exits unknown
    ("STN05", "Stadium Junction", "Blue Line", "interchange", 35000, True),
    ("STN06", "Lakeview", "Green Line", "elevated", 15000, True),
    ("STN07", "Airport Link", "Green Line", "underground", 22000, True),
    ("STN08", "Industrial Estate", "Red Line", "at-grade", 12000, True),
]

SPACE_TYPES = ["retail", "kiosk", "advertising_panel", "digital_screen"]
STATUSES = ["occupied", "vacant", "vacant", "under_maintenance", "unavailable"]

HOURS = list(range(6, 24))  # 06:00–23:00 service hours
# Relative demand weight per hour (morning & evening peaks).
HOUR_WEIGHTS = {
    6: 0.4,
    7: 0.9,
    8: 1.6,
    9: 1.8,
    10: 1.0,
    11: 0.8,
    12: 0.9,
    13: 0.9,
    14: 0.7,
    15: 0.8,
    16: 1.0,
    17: 1.6,
    18: 1.9,
    19: 1.7,
    20: 1.1,
    21: 0.7,
    22: 0.5,
    23: 0.3,
}
N_DAYS = 30


def build_dataset(seed: int = SEED) -> dict:
    rng = random.Random(seed)
    today = date(2026, 10, 1)  # fixed anchor for reproducibility
    start = today - timedelta(days=N_DAYS - 1)

    stations = [
        {"code": c, "name": n, "line": ln, "station_type": t, "location_description": None}
        for (c, n, ln, t, _scale, _ek) in STATIONS
    ]

    footfall: list[dict] = []
    for code, _n, _ln, _t, scale, exits_known in STATIONS:
        for d in range(N_DAYS):
            day = start + timedelta(days=d)
            weekend = day.weekday() >= 5
            day_factor = 0.75 if weekend else 1.0
            for h in HOURS:
                base = scale / len(HOURS) * HOUR_WEIGHTS[h] * day_factor
                entries = max(0, int(rng.gauss(base, base * 0.18)))
                rec = {
                    "station_code": code,
                    "observation_date": day.isoformat(),
                    "hour": h,
                    "entries": entries,
                    "exits": int(entries * rng.uniform(0.82, 0.98)) if exits_known else None,
                    "source": "synthetic-generator",
                }
                footfall.append(rec)

    spaces: list[dict] = []
    leases: list[dict] = []
    for code, _n, _ln, _t, _scale, _ek in STATIONS:
        n_spaces = rng.randint(4, 7)
        for i in range(n_spaces):
            stype = rng.choice(SPACE_TYPES)
            status = rng.choice(STATUSES)
            unit_priced = stype in ("advertising_panel", "digital_screen")
            # Area: unit-priced inventory often has no sqm; occasionally missing elsewhere.
            if unit_priced:
                area = None if rng.random() < 0.7 else round(rng.uniform(2, 8), 2)
            else:
                area = None if rng.random() < 0.1 else round(rng.uniform(8, 60), 2)
            visibility = None if rng.random() < 0.12 else round(rng.uniform(3, 10), 1)
            asking = None
            if status == "vacant" and rng.random() < 0.85:
                asking = float(rng.randint(20, 180) * 1000)
            space_code = f"{code}-S{i + 1:02d}"
            spaces.append(
                {
                    "station_code": code,
                    "space_code": space_code,
                    "space_type": stype,
                    "area_sqm": area,
                    "floor_description": rng.choice(
                        ["Concourse", "Platform", "Entrance A", "Entrance B"]
                    ),
                    "visibility_score": visibility,
                    "status": status,
                    "asking_monthly_rent": asking,
                    "available_from": None
                    if status != "vacant"
                    else (today + timedelta(days=rng.randint(0, 45))).isoformat(),
                }
            )
            if status == "occupied":
                leases.append(
                    {
                        "space_code": space_code,
                        "tenant_name": rng.choice(
                            ["Chai Point", "QuickMart", "AdWorks", "BookNook", "StyleHub"]
                        )
                        + f" #{rng.randint(1, 99)}",
                        "monthly_rent": float(rng.randint(25, 200) * 1000),
                        "start_date": (today - timedelta(days=rng.randint(60, 400))).isoformat(),
                        "end_date": None,
                        "status": "active",
                        "notes": "synthetic lease",
                    }
                )

    pricing_config = {
        "version": "v1.0-heuristic",
        "is_active": True,
        "base_rate_per_sqm": 1800.0,
        "base_panel_rate": 45000.0,
        "reference_daily_footfall": 20000,
        "footfall_elasticity": 0.3,
        "min_footfall_factor": 0.6,
        "max_footfall_factor": 1.8,
        "reference_visibility": 5.0,
        "visibility_weight": 0.08,
        "min_visibility_factor": 0.7,
        "max_visibility_factor": 1.4,
        "space_type_multipliers": {
            "retail": 1.0,
            "kiosk": 0.85,
            "advertising_panel": 1.2,
            "digital_screen": 1.5,
        },
        "source_notes": "Indicative assumptions for the Phase 1 demo; not market-verified.",
    }

    return {
        "_label": DATASET_LABEL,
        "_seed": seed,
        "stations": stations,
        "footfall": footfall,
        "spaces": spaces,
        "leases": leases,
        "pricing_config": pricing_config,
    }


def main() -> None:
    data = build_dataset()
    out_dir = Path(__file__).resolve().parents[1] / "data" / "sample"
    out_dir.mkdir(parents=True, exist_ok=True)
    for key in ("stations", "footfall", "spaces", "leases"):
        (out_dir / f"{key}.json").write_text(json.dumps(data[key], indent=2))
    (out_dir / "pricing_config.json").write_text(json.dumps(data["pricing_config"], indent=2))
    (out_dir / "README.txt").write_text(
        f"{DATASET_LABEL}\nseed={data['_seed']}\n"
        f"stations={len(data['stations'])} footfall_rows={len(data['footfall'])} "
        f"spaces={len(data['spaces'])} leases={len(data['leases'])}\n"
    )
    print(f"Wrote synthetic sample data to {out_dir}")
    print(
        f"stations={len(data['stations'])} footfall={len(data['footfall'])} "
        f"spaces={len(data['spaces'])} leases={len(data['leases'])}"
    )


if __name__ == "__main__":
    main()
