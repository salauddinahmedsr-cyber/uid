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
        # সার্ভারের জন্য headless=True অবশ্যই লাগবে
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto("https://www.midasbuy.com/midasbuy/bd/redeem/pubgm", wait_until="networkidle", timeout=60000)
            
            # কুকিজ একসেপ্ট
            try:
                accept = await page.wait_for_selector('text="Accept All"', timeout=5000)
                if accept: await accept.click()
            except: pass

            # আইডি ইনপুট
            id_btn = await page.wait_for_selector('text="Enter Your Player ID Now"', timeout=10000)
            await id_btn.click()
            
            input_box = await page.wait_for_selector('input[placeholder*="Player ID"]', timeout=5000)
            await input_box.fill(uid)
            await page.keyboard.press("Enter")
            
            await asyncio.sleep(6) # নাম লোড হওয়ার সময়
            
            nickname = ""
            # নতুন যে ক্লাসটি আপনি খুঁজে পেয়েছিলেন
            el = await page.query_selector('span[class*="UserTabBox_name"]')
            if el:
                nickname = await el.inner_text()
            
            await browser.close()
            return {"status": "success", "nickname": nickname.strip() if nickname else "Not Found"}

        except Exception as e:
            await browser.close()
            return {"status": "error", "message": str(e)[:50]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)