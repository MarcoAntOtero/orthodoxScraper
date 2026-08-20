"""
Fetches a given day's Vespers page from GOARCH's Digital Chant Stand and
saves it as a PDF, the same way "open the page, Ctrl+P, save as PDF"

Usage:
    python download_weekly_pdf.py 2026 4 28
"""

import sys

from playwright.sync_api import sync_playwright


def download_vespers_pdf(year: int, month: int, day: int, output_path: str) -> None:
    url = f"https://dcs.goarch.org/goa/dcs/h/s/{year}/{month:02d}/{day:02d}/ve/en/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="load", timeout=60000) 
        # The page's content (Greek text, hymn text) can still be settling
        # in via JS after "load" fires -- give it a moment before printing.
        page.wait_for_timeout(2000)

        # print_background=True keeps any print-specific styling the site
        # applies (colors, layout) instead of falling back to a plain
        # black-and-white render.
        page.pdf(path=output_path, print_background=True)

        browser.close()

    print(f"Wrote {output_path}")

