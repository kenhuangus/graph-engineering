"""Behavioral tests for the Chapter 6 message-graph listing."""
from ch06_workers_messages import PACKET, run_message_graph, run_shared_dict_bug


def test_message_graph_keeps_claims_caveats_and_flappy_hole() -> None:
    brief = run_message_graph(PACKET)
    assert brief.claims
    assert brief.caveats
    assert any("90.2" in c for c in brief.citations)
    assert any("Flappy Bird" in h for h in brief.holes)


def test_shared_dict_last_write_wins() -> None:
    state = run_shared_dict_bug(PACKET)
    assert state["notes"].startswith("B:")
    assert "A's notes are gone" in state["notes"]
