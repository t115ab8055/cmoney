from datetime import datetime


def parse_json_reactions(article: dict) -> dict[str, int]:
    emoji_names = {
        "like": "讚",
        "laugh": "哈",
        "money": "賺",
        "shock": "哇",
        "cry": "嗚嗚",
        "think": "真的嗎",
        "angry": "怒",
    }

    emoji_count = article.get("emojiCount", {})

    return {name: emoji_count.get(code, 0) for code, name in emoji_names.items()}


def parse_json_post_field(articles: list[dict]) -> dict[str, dict]:

    parse_data = {}
    for article in articles:
        article_id = str(article["id"])
        content = article.get("content", {})

        # API 的 createTime 是毫秒 timestamp
        create_time = article.get("createTime")

        created_at = None
        if create_time:
            create_time = datetime.fromtimestamp(  # noqa: DTZ006
                create_time / 1000
            )

            created_at = create_time.strftime("%Y/%m/%d %H:%M:%S")

        parse_data[article_id] = {
            "article_id": article_id,
            "author_id": str(article.get("creatorId"))
            if article.get("creatorId") is not None
            else None,
            "create_time": create_time,
            "created_at": created_at,
            "title": content.get("title"),
            "stocks": [
                {
                    "code": tag.get("key"),
                    "name": 0,
                }
                for tag in content.get("commodityTags", [])
                if tag.get("type") == "Stock"
            ],
            "content": content.get("text", ""),
            "donate_points": article.get("donation", 0),
            "comment_count": article.get("commentCount", 0),
            "reactions": parse_json_reactions(article),
        }

    return parse_data
