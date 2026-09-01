"""Behavioral tests for the Chapter 11 authz reachability listing."""
from chapter11_authz_reachability import bypass_refund, fanout_blast, governed_refund


def test_governed_refund_is_gated():
    g = governed_refund()
    assert g.is_gated("issue_refund")
    assert "issue_refund" in g.blast_radius("analyze_complaint")
    assert any(n.startswith("gated:") for n in g.findings())


def test_bypass_names_the_path():
    notes = bypass_refund().findings()
    assert any("bypass:" in n for n in notes)
    assert any(
        "START → fetch_history → analyze_complaint → issue_refund" in n for n in notes
    )


def test_fanout_blast_includes_apply():
    fan = fanout_blast()
    assert "apply" in fan.blast_radius("scout")
    assert any("bypass:" in n for n in fan.findings())
