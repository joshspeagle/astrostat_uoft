import os
import sys, asyncio
from playwright.async_api import async_playwright

def _launch(p):
    """Playwright's own browser resolution, unless PW_CHROMIUM names an executable."""
    exe = os.environ.get("PW_CHROMIUM")
    return p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()

async def main(html, png, w, h, full):
    async with async_playwright() as p:
        b = await _launch(p)
        pg = await b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        await pg.goto("file://" + html)
        await pg.wait_for_timeout(700)
        await pg.screenshot(path=png, full_page=full)
        await b.close()

if __name__ == "__main__":
    html, png = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]); h = int(sys.argv[4]); full = sys.argv[5] == "full"
    asyncio.run(main(html, png, w, h, full))
