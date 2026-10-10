from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from app.services.pricing_service import (
    assumptions_from_settings,
    estimate_price,
    validate_assumptions,
)

A = assumptions_from_settings()


def test_normal_pricing_is_available_and_bounded():
    r = estimate_price("retail", Decimal("25"), Decimal("7"), 30000.0, A)
    assert r.available is True
    assert r.indicative_monthly_price > 0
    assert r.indicative_annual_price == r.indicative_monthly_price * 12
    assert r.data_quality == "high"


def test_zero_footfall_clamps_to_min_factor():
    r = estimate_price("retail", Decimal("25"), Decimal("5"), 0.0, A)
    ff = next(f.value for f in r.factors if f.name == "footfall_factor")
    assert ff == A.min_footfall_factor


def test_missing_area_for_area_priced_is_unavailable():
    r = estimate_price("retail", None, Decimal("7"), 30000.0, A)
    assert r.available is False
    assert r.indicative_monthly_price is None
    assert any("area" in lim for lim in r.limitations)


def test_unit_priced_without_area_is_available():
    r = estimate_price("advertising_panel", None, Decimal("8"), 30000.0, A)
    assert r.available is True
    assert r.indicative_monthly_price > 0


def test_missing_visibility_uses_neutral_factor_and_lowers_quality():
    r = estimate_price("retail", Decimal("25"), None, 30000.0, A)
    vf = next(f.value for f in r.factors if f.name == "visibility_factor")
    assert vf == 1.0
    assert r.data_quality in ("medium", "low")


def test_extreme_footfall_clamped_to_max():
    r = estimate_price("retail", Decimal("25"), Decimal("5"), 10_000_000.0, A)
    ff = next(f.value for f in r.factors if f.name == "footfall_factor")
    assert ff == A.max_footfall_factor


def test_currency_is_rounded_to_whole_rupees():
    r = estimate_price("retail", Decimal("25"), Decimal("7"), 30000.0, A)
    assert r.indicative_monthly_price == r.indicative_monthly_price.quantize(Decimal("1"))


def test_results_are_repeatable():
    r1 = estimate_price("digital_screen", Decimal("4"), Decimal("9"), 40000.0, A)
    r2 = estimate_price("digital_screen", Decimal("4"), Decimal("9"), 40000.0, A)
    assert r1.indicative_monthly_price == r2.indicative_monthly_price


def test_invalid_configuration_raises():
    bad = replace(A, min_footfall_factor=2.0, max_footfall_factor=1.0)
    with pytest.raises(ValueError):
        validate_assumptions(bad)
    bad2 = replace(A, reference_daily_footfall=0)
    with pytest.raises(ValueError):
        estimate_price("retail", Decimal("10"), Decimal("5"), 100.0, bad2)


def test_no_footfall_data_does_not_fabricate():
    r = estimate_price("retail", Decimal("25"), Decimal("7"), None, A)
    ff = next(f.value for f in r.factors if f.name == "footfall_factor")
    assert ff == 1.0
    assert any("footfall" in lim for lim in r.limitations)
