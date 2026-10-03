from playwright.sync_api import Playwright, sync_playwright

from post import parse_json_post_field

stop_scroll = False
records = {}
def handle_response(response):
    global stop_scroll
    global records

    if "api/mach/api/Article/Stocks" in response.url:
        data = response.json()
        print(response.url)
        print(f"更新 {len(data["articles"])} 筆", end="")

        stop_scroll, parse_data = parse_json_post_field(articles=data["articles"])
        records.update(parse_data)

        print(f"，已累積 {len(records)} 筆")

def run(playwright: Playwright):
    browser = playwright.webkit.launch(headless=False)
    context = browser.new_context()
    page = browser.new_page()
    page.on("response", handle_response)
    # page.goto("https://www.cmoney.tw/forum/stock/6214")
    page.goto("https://www.cmoney.tw/forum/stock/2317")
    page.locator('iframe[title="「使用 Google 帳戶登入」對話方塊"]').content_frame.get_by_role(
        "button", name="關閉"
    ).click()
    page.locator(".sort__selected").click()
    page.get_by_text("最新", exact=True).click()

    while not stop_scroll:
        page.mouse.wheel(0, 3000)
        # page.wait_for_timeout(1)

    context.close()
    browser.close()

    import json
    with open("output/records.json", "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4,
        )

import time

start_time = time.perf_counter()
with sync_playwright() as playwright:
    run(playwright)

end_time = time.perf_counter()
elapsed_time = time.perf_counter() - start_time
minutes, seconds = divmod(elapsed_time, 60)

print(
    f"總共所花費時間為 {int(minutes)} 分 {seconds:.2f} 秒"
)