#!/usr/bin/env python3
"""Tests for bsky_build_queue.py.

Three real defects these lock down, all found by reading the live queue:

  1. The sent log has two shapes. scheduler.js writes
     "ISO | uri | tag | text"; bluesky.js wrote "ISO | uri | text". The reader
     required exactly four fields, so every line the standalone poster wrote was
     invisible and its text stayed in the draft pool — a repost of live copy.
  2. build_plan() excluded only PENDING queue entries from the pool
     (`not item.get("posted")`), which put already-published drafts straight back
     in and offered them up to be staged again.
  3. cmd_arm() appended every pending staging row without checking the live
     queue, so arming a rebuilt staging file duplicated slots that were already
     queued. The video builder always checked this; the text builder did not.

Run: python3 -m pytest test_bsky_build_queue.py -q
     (from the ape-social-machine directory)
"""

import json

import pytest

import bsky_build_queue as bq


# ---------------------------------------------------------------------------
# Sent log parsing
# ---------------------------------------------------------------------------

def test_four_field_scheduler_line_yields_the_text():
    line = "2026-09-20T05:47:08.585Z | at://did:plc:x/app.bsky.feed.post/1 | root | Volatility is not a risk."
    assert bq.text_from_log_line(line) == "Volatility is not a risk."


def test_three_field_bluesky_line_yields_the_text():
    line = "2026-09-18T20:02:00.000Z | at://did:plc:x/app.bsky.feed.post/2 | Retail investors do not lose because they are dumb."
    assert bq.text_from_log_line(line) == "Retail investors do not lose because they are dumb."


def test_reply_tag_is_stripped_but_the_text_survives():
    line = "2026-09-20T06:00:00.000Z | at://did:plc:x/app.bsky.feed.post/3 | reply_to=at://did:plc:y/app.bsky.feed.post/9 | Great question."
    assert bq.text_from_log_line(line) == "Great question."


def test_failed_tag_is_stripped():
    line = "2026-09-20T06:00:00.000Z | failed | failed | Something that never went out."
    assert bq.text_from_log_line(line) == "Something that never went out."


def test_a_text_containing_a_pipe_is_not_truncated():
    line = "2026-09-20T06:00:00.000Z | at://did:plc:x/app.bsky.feed.post/4 | open | cash | close is the whole idea."
    assert bq.text_from_log_line(line) == "open | cash | close is the whole idea."


def test_blank_and_short_lines_are_ignored():
    assert bq.text_from_log_line("") is None
    assert bq.text_from_log_line("\n") is None
    assert bq.text_from_log_line("just one field") is None


def test_load_sent_texts_reads_both_shapes(tmp_path, monkeypatch):
    log = tmp_path / "bsky_posts_sent.txt"
    log.write_text(
        "2026-09-20T05:47:08.585Z | at://a | root | Posted by the scheduler.\n"
        "2026-09-18T20:02:00.000Z | at://b | Posted by the standalone poster.\n"
        "2026-09-20T06:00:00.000Z | at://c | reply_to=at://z | A reply.\n"
    )
    monkeypatch.setattr(bq, "SENT_LOG", str(log))
    sent = bq.load_sent_texts()
    assert sent == {
        bq.norm("Posted by the scheduler."),
        bq.norm("Posted by the standalone poster."),
        bq.norm("A reply."),
    }


def test_load_sent_texts_without_a_log_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(bq, "SENT_LOG", str(tmp_path / "missing.txt"))
    assert bq.load_sent_texts() == set()


# ---------------------------------------------------------------------------
# Draft pool / plan dedup
# ---------------------------------------------------------------------------

def _write_drafts(tmp_path, count):
    """A drafts_bulk.json with `count` usable Bluesky drafts."""
    posts = [{"id": f"d{i}", "voice": "blitz", "text": f"Draft number {i} about reading filings properly."}
             for i in range(count)]
    path = tmp_path / "drafts_bulk.json"
    path.write_text(json.dumps({"bluesky": posts}))
    return path


def _point_module_at(tmp_path, monkeypatch, drafts="drafts_bulk.json"):
    monkeypatch.setattr(bq, "HERE", str(tmp_path))
    monkeypatch.setattr(bq, "DRAFT_FILES", [drafts])
    monkeypatch.setattr(bq, "STAGING", str(tmp_path / "bsky_queue_staging.json"))
    monkeypatch.setattr(bq, "LIVE", str(tmp_path / "bsky_scheduled_posts.json"))
    monkeypatch.setattr(bq, "SENT_LOG", str(tmp_path / "bsky_posts_sent.txt"))


def test_an_already_posted_draft_is_never_restaged(tmp_path, monkeypatch):
    """The inversion: excluding only pending items put posted copy back in."""
    _point_module_at(tmp_path, monkeypatch)
    _write_drafts(tmp_path, 60)
    live = tmp_path / "bsky_scheduled_posts.json"
    live.write_text(json.dumps([
        {"at": "2026-09-20T13:00:00Z", "text": "Draft number 0 about reading filings properly.",
         "kind": "root", "posted": True, "posted_at": "2026-09-20T13:00:00Z", "uri": "at://x"},
    ]))

    plan = bq.build_plan(days=1)
    staged = {bq.norm(p["text"]) for p in plan}
    assert bq.norm("Draft number 0 about reading filings properly.") not in staged


def test_a_pending_queue_entry_is_never_restaged(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    _write_drafts(tmp_path, 60)
    (tmp_path / "bsky_scheduled_posts.json").write_text(json.dumps([
        {"at": "2026-09-25T13:00:00Z", "text": "Draft number 1 about reading filings properly.",
         "kind": "root", "posted": False},
    ]))

    plan = bq.build_plan(days=1)
    assert bq.norm("Draft number 1 about reading filings properly.") not in {bq.norm(p["text"]) for p in plan}


def test_a_sent_log_entry_is_never_restaged(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    _write_drafts(tmp_path, 60)
    (tmp_path / "bsky_posts_sent.txt").write_text(
        "2026-09-18T20:02:00.000Z | at://b | Draft number 2 about reading filings properly.\n"
    )

    plan = bq.build_plan(days=1)
    assert bq.norm("Draft number 2 about reading filings properly.") not in {bq.norm(p["text"]) for p in plan}


def test_the_plan_is_the_expected_shape(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    _write_drafts(tmp_path, 60)
    plan = bq.build_plan(days=1)
    assert len(plan) == bq.POSTS_PER_DAY
    assert len({bq.norm(p["text"]) for p in plan}) == len(plan)
    assert all(p["at_utc"].endswith("Z") for p in plan)


# ---------------------------------------------------------------------------
# Arm idempotency
# ---------------------------------------------------------------------------

def _staged_plan(slots=3):
    return [
        {"at_local": f"2026-09-25T{9 + i:02d}:00:00-04:00",
         "at_utc": f"2026-09-25T{13 + i:02d}:00:00Z",
         "text": f"Staged post {i}.",
         "source": f"drafts_bulk.json#d{i}"}
        for i in range(slots)
    ]


def test_arming_twice_does_not_duplicate_the_queue(tmp_path, monkeypatch, capsys):
    _point_module_at(tmp_path, monkeypatch)
    staging = tmp_path / "bsky_queue_staging.json"
    staging.write_text(json.dumps(_staged_plan()))
    live = tmp_path / "bsky_scheduled_posts.json"
    live.write_text("[]")

    bq.cmd_arm()
    assert len(json.loads(live.read_text())) == 3

    # A rebuilt staging file (queued flags gone) must not re-add the same slots.
    staging.write_text(json.dumps(_staged_plan()))
    bq.cmd_arm()
    out = capsys.readouterr().out
    assert len(json.loads(live.read_text())) == 3, "arming twice duplicated the queue"
    assert "already present, skipped" in out


def test_arming_skips_a_slot_already_in_the_live_queue(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    (tmp_path / "bsky_queue_staging.json").write_text(json.dumps(_staged_plan()))
    live = tmp_path / "bsky_scheduled_posts.json"
    live.write_text(json.dumps([
        {"at": "2026-09-25T13:00:00Z", "text": "Staged post 0.", "kind": "root",
         "target_uri": None, "posted": False, "posted_at": None, "uri": None, "error": None},
    ]))

    bq.cmd_arm()
    rows = json.loads(live.read_text())
    assert len(rows) == 3, "the overlapping slot was added a second time"
    assert sum(1 for r in rows if r["at"] == "2026-09-25T13:00:00Z") == 1


def test_arming_marks_every_staged_row_queued(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    staging = tmp_path / "bsky_queue_staging.json"
    staging.write_text(json.dumps(_staged_plan()))
    (tmp_path / "bsky_scheduled_posts.json").write_text("[]")

    bq.cmd_arm()
    assert all(p["queued"] for p in json.loads(staging.read_text()))

    # Second call has nothing pending and must say so.
    bq.cmd_arm()


def test_arming_with_no_staging_file_is_refused(tmp_path, monkeypatch):
    _point_module_at(tmp_path, monkeypatch)
    with pytest.raises(SystemExit):
        bq.cmd_arm()
