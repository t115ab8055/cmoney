import csv
import json


def export_csv(code, records):
    fieldnames = [
        "文章 ID",
        "創建者 ID",
        "創建時間",
        "標題",
        "標記的股票",
        "文章內容",
        "被donate P點",
        "評論數",
        "回應表情 讚",
        "回應表情 哈",
        "回應表情 賺",
        "回應表情 哇",
        "回應表情 嗚嗚",
        "回應表情 真的嗎",
        "回應表情 怒",
    ]

    with open(f"output/{code}.csv", "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records.values():
            stocks = [[stock["code"], stock["name"]] for stock in record.get("stocks", [])]

            reactions = record.get("reactions", {})

            writer.writerow(
                {
                    "文章 ID": record.get("article_id"),
                    "創建者 ID": record.get("author_id"),
                    "創建時間": record.get("created_at"),
                    "標題": record.get("title"),
                    "標記的股票": str(stocks),
                    "文章內容": record.get("content"),
                    "被donate P點": record.get("donate_points", 0),
                    "評論數": record.get("comment_count", 0),
                    "回應表情 讚": reactions.get("讚", 0),
                    "回應表情 哈": reactions.get("哈", 0),
                    "回應表情 賺": reactions.get("賺", 0),
                    "回應表情 哇": reactions.get("哇", 0),
                    "回應表情 嗚嗚": reactions.get("嗚嗚", 0),
                    "回應表情 真的嗎": reactions.get("真的嗎", 0),
                    "回應表情 怒": reactions.get("怒", 0),
                }
            )


def export_json(code, records):
    with open(f"output/{code}.json", "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4,
        )
