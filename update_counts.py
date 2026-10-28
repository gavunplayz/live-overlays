import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "counts.json"


def request_json(url, headers=None, data=None):
    request = urllib.request.Request(url, headers=headers or {}, data=data)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def get_youtube_subscribers():
    api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY GitHub Actions secret")
    query = urllib.parse.urlencode({
        "part": "statistics",
        "forHandle": "GP48YT",
        "key": api_key,
    })
    result = request_json("https://www.googleapis.com/youtube/v3/channels?" + query)
    items = result.get("items", [])
    if not items:
        raise RuntimeError("YouTube channel @GP48YT was not found or the API key is invalid")
    stats = items[0].get("statistics", {})
    if stats.get("hiddenSubscriberCount"):
        raise RuntimeError("The YouTube subscriber count is hidden")
    return int(stats["subscriberCount"])


def get_twitch_followers():
    client_id = os.environ.get("TWITCH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("TWITCH_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("Missing TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET GitHub Actions secret")

    token_body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode("utf-8")
    token_result = request_json(
        "https://id.twitch.tv/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=token_body,
    )
    access_token = token_result["access_token"]
    common_headers = {
        "Client-Id": client_id,
        "Authorization": "Bearer " + access_token,
    }

    user_query = urllib.parse.urlencode({"login": "gavunplayz"})
    users = request_json("https://api.twitch.tv/helix/users?" + user_query, headers=common_headers)
    user_list = users.get("data", [])
    if not user_list:
        raise RuntimeError("Twitch channel gavunplayz was not found")
    broadcaster_id = user_list[0]["id"]

    followers_query = urllib.parse.urlencode({"broadcaster_id": broadcaster_id, "first": 1})
    followers = request_json(
        "https://api.twitch.tv/helix/channels/followers?" + followers_query,
        headers=common_headers,
    )
    if "total" not in followers:
        raise RuntimeError("Twitch did not return a follower total; check API authorization")
    return int(followers["total"])


def main():
    previous = {}
    if OUTPUT.exists():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except Exception:
            previous = {}

    result = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "youtube": {"subscribers": previous.get("youtube", {}).get("subscribers")},
        "twitch": {"followers": previous.get("twitch", {}).get("followers")},
        "error": None,
    }
    failures = []

    try:
        result["youtube"]["subscribers"] = get_youtube_subscribers()
    except Exception as exc:
        failures.append("YouTube: " + str(exc))

    try:
        result["twitch"]["followers"] = get_twitch_followers()
    except Exception as exc:
        failures.append("Twitch: " + str(exc))

    if failures:
        result["error"] = " | ".join(failures)
        print(result["error"], file=sys.stderr)

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    # Keep the workflow marked failed if either data source failed, but preserve
    # the last known value for the platform that could not be refreshed.
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
