from playwright.sync_api import Playwright, sync_playwright

from post import collect_posts, get_posts

# 儲存已收集的文章，key 暫時使用文章文字
records = {}


def run(playwright: Playwright) -> None:
    browser = playwright.webkit.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.cmoney.tw/forum/stock/6214")
    page.locator('iframe[title="「使用 Google 帳戶登入」對話方塊"]').content_frame.get_by_role(
        "button", name="關閉"
    ).click()
    page.locator(".sort__selected").click()
    page.get_by_text("最新", exact=True).click()

    posts = get_posts(page=page)
    posts.first.hover()

    collect_posts(page=page, posts=posts, records=records)
    for _ in range(1):
        # page.mouse.wheel(0, 5000)
        # page.wait_for_timeout(1500)

        posts = get_posts(page=page)

        # page.pause()
        collect_posts(page=page, posts=posts, records=records)

    # 顯示所有已收集的內容
    for index, record in enumerate(records.values(), 1):
        print(f"\n----- 第 {index} 筆 -----")
        print(record["title"], record["content"])

    print(f"\n總共收集：{len(records)} 筆")

    page.close()


with sync_playwright() as playwright:
    run(playwright)
