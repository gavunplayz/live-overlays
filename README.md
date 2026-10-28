# GP48 Live Counters

A transparent OBS browser overlay for the YouTube subscriber count on `@GP48YT` and the Twitch follower count on `gavunplayz`.

## Files

- `index.html` — transparent overlay for OBS.
- `counts.json` — latest published counts, refreshed by GitHub Actions.
- `update_counts.py` — fetches counts from YouTube and Twitch.
- `.github/workflows/update-counts.yml` — refreshes the data every five minutes and can also be run manually.

## One-time setup

### 1. Create API credentials

**YouTube**
1. Open the Google Cloud Console and create/select a project.
2. Enable **YouTube Data API v3**.
3. Create an API key. Restrict it to YouTube Data API v3 where possible.
4. Add the key to this repository as the Actions secret `YOUTUBE_API_KEY`.

**Twitch**
1. Open the Twitch Developer Console and register an application.
2. Copy its Client ID and generate a Client Secret.
3. Add these repository Actions secrets:
   - `TWITCH_CLIENT_ID`
   - `TWITCH_CLIENT_SECRET`

Never put API secrets in `index.html`, `update_counts.py`, or any other public file.

### 2. Add GitHub Actions secrets

In the repository, open **Settings → Secrets and variables → Actions → New repository secret** and add the three names above exactly.

### 3. Enable GitHub Pages

Open **Settings → Pages** and set the build source to **Deploy from a branch**, branch **main**, folder **/(root)**. Save.

The overlay URL should then be:

`https://gavunplayz.github.io/live-overlays/`

### 4. Run the first update

Open **Actions → Update social counters → Run workflow**. Check the run logs. A successful run updates `counts.json`. Scheduled updates run every five minutes, although GitHub may delay scheduled jobs during busy periods.

If the Twitch API rejects the app access token for the follower-count endpoint, the workflow will show the API error in its logs; the Twitch authorization method will need to be adjusted before that counter can update.

## OBS setup

1. Add a **Browser Source** in OBS.
2. Set its URL to the overlay URL above.
3. Set a canvas-friendly width and height (for example, 600 × 260).
4. Keep the background transparent.

Optional URL parameters:
- `?youtube=0` hides the YouTube counter.
- `?twitch=0` hides the Twitch counter.
- `?youtube=0&twitch=1` shows Twitch only.

The page checks for newly published count data every 30 seconds. The official API data itself is refreshed by the scheduled GitHub Action, so changes are not instantaneous. YouTube may round subscriber totals to three significant figures.
