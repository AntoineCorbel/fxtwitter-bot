"""Tests for the URL rewriting logic in main.rewrite_message."""

import pytest

from main import _guild_entry, rewrite_message


# ----------------------------------------------------------------- basic swap


def test_rewrites_x_com_url():
    result = rewrite_message("check this https://x.com/user/status/123")
    assert result == "check this https://fxtwitter.com/user/status/123"


def test_rewrites_twitter_com_url():
    result = rewrite_message("https://twitter.com/user/status/1")
    assert result == "https://fxtwitter.com/user/status/1"


def test_preserves_www_prefix():
    result = rewrite_message("https://www.x.com/a/b")
    assert result == "https://www.fxtwitter.com/a/b"


# ------------------------------------------------------------- no-op behavior


def test_returns_none_when_no_x_url():
    assert rewrite_message("just plain text") is None


def test_returns_none_for_unrelated_urls():
    assert rewrite_message("https://example.com/foo") is None


def test_returns_none_for_empty_string():
    assert rewrite_message("") is None


# --------------------------------------------------------------- edge cases


def test_rewrites_multiple_urls_in_one_message():
    result = rewrite_message("https://x.com/a and https://twitter.com/b")
    assert result == "https://fxtwitter.com/a and https://fxtwitter.com/b"


def test_preserves_query_string():
    result = rewrite_message("https://x.com/a/b?c=1&d=2")
    assert result == "https://fxtwitter.com/a/b?c=1&d=2"


def test_preserves_surrounding_text():
    result = rewrite_message("look at this https://x.com/foo lol")
    assert result == "look at this https://fxtwitter.com/foo lol"


@pytest.mark.parametrize("scheme", ["http", "https"])
def test_handles_both_schemes(scheme):
    result = rewrite_message(f"{scheme}://x.com/post")
    assert result == f"{scheme}://fxtwitter.com/post"


def test_case_insensitive_host():
    result = rewrite_message("https://X.COM/Foo")
    assert result is not None
    assert "fxtwitter.com/Foo" in result


def test_does_not_match_subdomain_lookalike():
    # notx.com should not be rewritten — only x.com / twitter.com hosts.
    assert rewrite_message("https://notx.com/foo") is None


# --------------------------------------------------------------- guild mode


def test_new_guild_defaults_to_delete_mode():
    assert _guild_entry({}, "1")["mode"] == "delete"


def test_legacy_guild_without_mode_gets_delete_default():
    # Entries written before the mode setting existed must not crash.
    data = {"1": {"conversions": 5, "today": 2, "day": None}}
    assert _guild_entry(data, "1")["mode"] == "delete"


def test_existing_mode_is_preserved():
    data = {"1": {"conversions": 0, "today": 0, "day": None, "mode": "suppress"}}
    assert _guild_entry(data, "1")["mode"] == "suppress"
