from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import uvicorn
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/check")
async def check_uid(uid: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # ইমেজ এবং অপ্রয়োজনীয় জিনিস ব্লক করা (স্পিড বাড়ানোর জন্য)
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css}", lambda route: route.abort())

        try:
            # সরাসরি আইডি সাবমিট করার চেষ্টা
            url = f"https://www.midasbuy.com/midasbuy/bd/redeem/pubgm"
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # ইনপুট বক্সের জন্য অপেক্ষা
            input_box = await page.wait_for_selector('input[placeholder*="Player ID"]', timeout=15000)
            await input_box.fill(uid)
            
            # এন্টার বা ওকে বাটন ক্লিক
            await page.keyboard.press("Enter")
            
            # নাম আসার জন্য অপেক্ষা
            nickname_selector = 'span[class*="UserTabBox_name"]'
            await page.wait_for_selector(nickname_selector, timeout=15000)
            
            el = await page.query_selector(nickname_selector)
            nickname = await el.inner_text() if el else "Not Found"

            await browser.close()
            return {"status": "success", "nickname": nickname.strip()}

        except Exception as e:
            await browser.close()
            return {"status": "error", "message": "Slow connection or ID not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
