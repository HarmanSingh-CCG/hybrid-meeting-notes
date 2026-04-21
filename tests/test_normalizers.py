"""Normalizer tests — cover each input format."""

from meeting_agent.models import MeetingMetadata
from meeting_agent.normalizers.json_ import normalize_json
from meeting_agent.normalizers.srt import normalize_srt
from meeting_agent.normalizers.txt import normalize_txt
from meeting_agent.normalizers.vtt import normalize_vtt


META = MeetingMetadata(title="Test")


def test_vtt_strips_header_timestamps_and_cue_ids():
    raw = """WEBVTT

1
00:00:00.000 --> 00:00:02.000
Alice: Hello

2
00:00:02.000 --> 00:00:04.000
Bob: Hi there
"""
    out = normalize_vtt(raw, META)
    assert "WEBVTT" not in out.text
    assert "-->" not in out.text
    assert "Alice: Hello" in out.text
    assert "Bob: Hi there" in out.text
    assert out.source_format == "vtt"


def test_srt_strips_cue_numbers_and_timestamps():
    raw = """1
00:00:00,000 --> 00:00:02,000
Alice: Hello

2
00:00:02,000 --> 00:00:04,000
Bob: Hi
"""
    out = normalize_srt(raw, META)
    assert "-->" not in out.text
    # Bare numeric lines removed
    assert "\n1\n" not in out.text
    assert "Alice: Hello" in out.text
    assert out.source_format == "srt"


def test_txt_passes_through_with_blank_line_cleanup():
    raw = "Alice: Hello\n\n\nBob: Hi\n"
    out = normalize_txt(raw, META)
    assert "Alice: Hello" in out.text
    assert "Bob: Hi" in out.text
    assert out.source_format == "txt"


def test_json_list_of_utterances():
    raw = '[{"speaker":"Alice","text":"Hello"},{"speaker":"Bob","text":"Hi"}]'
    out = normalize_json(raw, META)
    assert "Alice: Hello" in out.text
    assert "Bob: Hi" in out.text
    assert out.source_format == "json"


def test_json_object_with_segments_key():
    raw = '{"metadata":{"title":"Sync"},"segments":[{"speaker":"A","text":"ok"}]}'
    out = normalize_json(raw, META)
    assert "A: ok" in out.text
    # metadata.title should override the default META.title
    assert out.metadata.title == "Sync"
