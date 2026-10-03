from playwright.sync_api import Playwright, sync_playwright

from export import export_csv, export_json
from parse import parse_json_post_field

stop_scroll = False
records = {}


def block_resources(route):
    resource_type = route.request.resource_type
    route.abort() if resource_type in {"image"} else route.continue_()


def handle_response(response):
    global stop_scroll

    if "api/mach/api/Article/Stocks" in response.url:
        data = response.json()
        print(response.url)
        print(f"更新 {len(data['articles'])} 筆", end="")

        stop_scroll, parse_data = parse_json_post_field(articles=data["articles"])
        records.update(parse_data)

        print(f"，已累積 {len(records)} 筆")


def run(playwright: Playwright, code: str):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = browser.new_page()
    page.route("**/*", block_resources)
    page.on("response", handle_response)
    page.goto(f"https://www.cmoney.tw/forum/stock/{code}")
    # page.locator('iframe[title="「使用 Google 帳戶登入」對話方塊"]').content_frame.get_by_role(
    #     "button", name="關閉"
    # ).click()
    page.locator(".sort__selected").click()
    page.get_by_text("最新", exact=True).click()

    while not stop_scroll:
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(100)

    context.close()
    browser.close()


def main():
    global stop_scroll
    global records
    with sync_playwright() as playwright:
        for code in ["6214", "2317"]:
            run(playwright, code)
            export_json(code=code, records=records)
            export_csv(code=code, records=records)
            stop_scroll = False
            records = {}


if __name__ == "__main__":
    import time

    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    elapsed_time = time.perf_counter() - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    print(f"總共所花費時間為 {int(minutes)} 分 {seconds:.2f} 秒")
