"""Footfall analytics. Aggregations run in SQL; only small grouped result sets
are pulled into Python. `entries` is the demand measure; missing observations are
distinguished from genuine zeros via observation_count / coverage_ratio."""

from __future__ import annotations

from datetime import date

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db.models.footfall import FootfallRecord
from app.db.models.station import Station
from app.schemas.analytics import StationFootfallRank
from app.schemas.footfall import FootfallSummary


def _is_weekend(d: date) -> bool:
    return d.weekday() >= 5  # Sat=5, Sun=6


def _filters(station_id: int | None, start: date | None, end: date | None):
    conds = []
    if station_id is not None:
        conds.append(FootfallRecord.station_id == station_id)
    if start is not None:
        conds.append(FootfallRecord.observation_date >= start)
    if end is not None:
        conds.append(FootfallRecord.observation_date <= end)
    return conds


def footfall_summary(
    db: Session,
    station_id: int | None = None,
    start: date | None = None,
    end: date | None = None,
) -> FootfallSummary:
    conds = _filters(station_id, start, end)

    totals = db.execute(
        select(
            func.count(FootfallRecord.id),
            func.coalesce(func.sum(FootfallRecord.entries), 0),
            func.sum(FootfallRecord.exits),
            func.count(distinct(FootfallRecord.observation_date)),
            func.count(distinct(FootfallRecord.station_id)),
            func.min(FootfallRecord.observation_date),
            func.max(FootfallRecord.observation_date),
        ).where(*conds)
    ).one()
    (obs_count, total_entries, total_exits, distinct_days, station_scope, min_d, max_d) = totals
    total_entries = int(total_entries or 0)

    notes: list[str] = []
    if obs_count == 0:
        notes.append("no observations in the selected scope")
        return FootfallSummary(
            station_id=station_id,
            start_date=start,
            end_date=end,
            observation_count=0,
            distinct_days=0,
            total_entries=0,
            notes=notes,
        )

    # Hourly distribution + peak (grouped, max 24 rows)
    hourly_rows = db.execute(
        select(FootfallRecord.hour, func.sum(FootfallRecord.entries))
        .where(*conds)
        .group_by(FootfallRecord.hour)
    ).all()
    hourly = {int(h): int(s) for h, s in hourly_rows}
    peak_val = max(hourly.values())
    peak_hours = sorted(h for h, v in hourly.items() if v == peak_val)

    # Per-day entries for weekday/weekend split (grouped, small)
    day_rows = db.execute(
        select(FootfallRecord.observation_date, func.sum(FootfallRecord.entries))
        .where(*conds)
        .group_by(FootfallRecord.observation_date)
    ).all()
    wk_vals = [int(s) for d, s in day_rows if not _is_weekend(d)]
    we_vals = [int(s) for d, s in day_rows if _is_weekend(d)]
    weekday_avg = sum(wk_vals) / len(wk_vals) if wk_vals else None
    weekend_avg = sum(we_vals) / len(we_vals) if we_vals else None

    avg_hourly = total_entries / obs_count
    avg_daily = total_entries / distinct_days

    # Coverage: observed hour-slots vs expected over the span (best effort).
    coverage = None
    span_start = start or min_d
    span_end = end or max_d
    if span_start and span_end:
        expected_days = (span_end - span_start).days + 1
        expected = expected_days * 24 * max(station_scope, 1)
        if expected > 0:
            coverage = round(obs_count / expected, 4)
            if coverage < 1.0:
                notes.append("partial coverage: some hour-slots have no observation")

    return FootfallSummary(
        station_id=station_id,
        start_date=span_start,
        end_date=span_end,
        observation_count=int(obs_count),
        distinct_days=int(distinct_days),
        total_entries=total_entries,
        total_exits=int(total_exits) if total_exits is not None else None,
        avg_hourly_entries=round(avg_hourly, 2),
        avg_daily_entries=round(avg_daily, 2),
        peak_hour=peak_hours[0],
        peak_hour_entries=peak_val,
        peak_hours_tied=peak_hours,
        weekday_avg_daily_entries=round(weekday_avg, 2) if weekday_avg is not None else None,
        weekend_avg_daily_entries=round(weekend_avg, 2) if weekend_avg is not None else None,
        hourly_distribution=hourly,
        coverage_ratio=coverage,
        notes=notes,
    )


def observed_daily_footfall(db: Session, station_id: int) -> float | None:
    """Average daily entries for a station across all its observations, or None."""
    row = db.execute(
        select(
            func.coalesce(func.sum(FootfallRecord.entries), 0),
            func.count(distinct(FootfallRecord.observation_date)),
        ).where(FootfallRecord.station_id == station_id)
    ).one()
    total, days = int(row[0] or 0), int(row[1] or 0)
    if days == 0:
        return None
    return total / days


def station_ranking(
    db: Session, start: date | None = None, end: date | None = None
) -> list[StationFootfallRank]:
    conds = _filters(None, start, end)
    rows = db.execute(
        select(
            Station.id,
            Station.name,
            func.coalesce(func.sum(FootfallRecord.entries), 0),
            func.count(distinct(FootfallRecord.observation_date)),
        )
        .join(FootfallRecord, FootfallRecord.station_id == Station.id)
        .where(*conds)
        .group_by(Station.id, Station.name)
        .order_by(func.sum(FootfallRecord.entries).desc())
    ).all()
    result = []
    for rank, (sid, name, total, days) in enumerate(rows, start=1):
        total = int(total or 0)
        result.append(
            StationFootfallRank(
                station_id=sid,
                station_name=name,
                total_entries=total,
                avg_daily_entries=round(total / days, 2) if days else None,
                rank=rank,
            )
        )
    return result


def percentage_change(
    db: Session,
    station_id: int | None,
    a_start: date,
    a_end: date,
    b_start: date,
    b_end: date,
) -> dict:
    """Percentage change in total entries from baseline period A to period B.
    Returns pct_change=None when the baseline is zero (undefined), and flags
    unequal-length periods instead of silently comparing them."""

    def _total(s: date, e: date) -> int:
        row = db.execute(
            select(func.coalesce(func.sum(FootfallRecord.entries), 0)).where(
                *_filters(station_id, s, e)
            )
        ).one()
        return int(row[0] or 0)

    base = _total(a_start, a_end)
    curr = _total(b_start, b_end)
    len_a = (a_end - a_start).days + 1
    len_b = (b_end - b_start).days + 1
    notes = []
    if len_a != len_b:
        notes.append(
            f"periods differ in length ({len_a} vs {len_b} days); comparison is indicative"
        )
    pct = None if base == 0 else round((curr - base) / base * 100, 2)
    if base == 0:
        notes.append("baseline total is zero; percentage change is undefined (null)")
    return {
        "baseline_total": base,
        "current_total": curr,
        "pct_change": pct,
        "period_a": {"start": str(a_start), "end": str(a_end), "days": len_a},
        "period_b": {"start": str(b_start), "end": str(b_end), "days": len_b},
        "notes": notes,
    }
