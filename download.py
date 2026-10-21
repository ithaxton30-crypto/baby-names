import io
import re
import zipfile
import pandas as pd
import requests

URL = "https://www.ssa.gov/oact/babynames/names.zip"
OUTPUT_FILE = "ssa-baby-names.csv"

# Browser-like headers so ssa.gov allows the download
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.ssa.gov/oact/babynames/limits.html",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


def main():
    response = requests.get(URL, headers=HEADERS, timeout=60)
    response.raise_for_status()

    frames = []
    # Read the zip file directly from memory
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        for filename in sorted(zf.namelist()):
            match = re.match(r"yob(\d{4})\.txt$", filename)
            if not match:
                continue
            year = int(match.group(1))
            with zf.open(filename) as f:
                df = pd.read_csv(f, names=["name", "sex", "count"])
                df["year"] = year
                frames.append(df[["year", "name", "sex", "count"]])

    all_names = pd.concat(frames, ignore_index=True)
    all_names.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(all_names):,} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
