from __future__ import annotations

from dasef.features.direct_risk import parse_direct_risk_response


def test_parse_direct_risk_response_clips_to_probability_range() -> None:
    assert parse_direct_risk_response('{"direct_risk_score": 1.4}') == 1.0
    assert parse_direct_risk_response('{"direct_risk_score": -0.2}') == 0.0
    assert parse_direct_risk_response('prefix {"direct_risk_score": 0.25}') == 0.25
