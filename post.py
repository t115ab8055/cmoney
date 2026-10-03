from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def parse_reactions(page: Page, post: Locator) -> dict[str, int]:
    emoji_names = {
        "like": "讚",
        "happy": "哈",
        "money": "賺",
        "surprise": "哇",
        "sad": "嗚嗚",
        "confuse": "真的嗎",
        "angry": "怒",
    }

    reactions = dict.fromkeys(emoji_names.values(), 0)

    post.locator(".articleResponse__emoji").click(timeout=2000)
    page.locator(".articleModal__select:visible").click(timeout=3000)

    menu = page.locator(".articleModal__menu:visible")
    menu.wait_for(state="visible")

    for code, name in emoji_names.items():
        item = menu.locator(f'.articleModal__item:has(img[data-src*="icon_emoji_{code}."])')
        reactions[name] = int(item.locator(".articleModal__num").text_content().strip())

    page.get_by_role("button", name="Close", exact=True).click(timeout=2000)
    menu.wait_for(state="hidden", timeout=2000)

    return reactions


def parse_post_field(page: Page, post: Locator) -> dict[str, dict]:
    article = post.locator(".normal__info a")
    author = post.locator(".normal__popup a")
    title = post.locator("h3.articleContent__title")

    article_id = article.get_attribute("href", timeout=2000).split("/")[-1]

    return {
        article_id: {
            "article_id": article_id,
            "author_id": author.get_attribute("href", timeout=2000).split("/")[-1],
            "author_name": author.inner_text(timeout=2000).strip(),
            "created_at": article.inner_text(timeout=2000).strip(),
            "title": title.inner_text(timeout=2000).strip() if title.count() else None,
            "stocks": [
                {
                    "code": stock.get_attribute("href", timeout=2000).split("/")[-1],
                    "name": stock.inner_text(timeout=2000).strip(),
                }
                for stock in post.locator(".articleTags__btn[href*='/forum/stock/']").all()
            ],
            "content": "\n".join(
                post.locator(".articleContent__text .textRule__line > span").all_text_contents()
            ),
            "donate_points": int(
                post.locator(".articleResponse__donate")
                .inner_text(timeout=2000)
                .strip()
                .replace("P", "")
            ),
            "comment_count": int(
                post.locator(".articleResponse__comment")
                .inner_text(timeout=2000)
                .strip()
                .replace("則留言", "")
                .replace("則回答", "")
            ),
            "reactions": parse_reactions(
                page=page,
                post=post,
            ),
        }
    }


def collect_posts(page: Page, posts: Locator, records: dict[str, dict]) -> None:
    before_count = len(records)

    try:
        for index, post in enumerate(posts.all(), start=1):
            posts.nth(index).scroll_into_view_if_needed(timeout=2000)
            page.wait_for_timeout(1500)
            records.update(
                parse_post_field(
                    page=page,
                    post=post,
                )
            )
    except PlaywrightTimeoutError:
        target_post = posts.nth(index - 1)
        target_post.last.scroll_into_view_if_needed(timeout=2000)
        target_post.last.hover(timeout=2000)

        print(f"第 {index} 篇已失效，結束這一輪")
        print(f"新增：{len(records) - before_count} 筆｜累計：{len(records)} 筆")
        return

    print(f"新增：{len(records) - before_count} 筆｜累計：{len(records)} 筆")
    posts.last.scroll_into_view_if_needed(timeout=2000)
    posts.last.hover(timeout=2000)


def get_posts(page: Page) -> Locator:
    virtual_list = page.locator(".articleContainer__virtualList").first
    posts = virtual_list.locator(".articleVirtualItem")

    posts.first.wait_for(
        state="visible",
        timeout=10000,
    )

    return posts
