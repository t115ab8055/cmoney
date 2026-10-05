from datetime import datetime

import requests
import urllib3
from requests import Response

from cursor import calculate_cursor
from export import export_csv
from parse import parse_json_post_field

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_yearly_cursors(year: int) -> list:
    cursor = []
    for month in range(1, 12):
        cursor.append(calculate_cursor(year=year, month=month, day=1))
    return cursor


def get_parameter(code: str) -> tuple[str, dict[str, str], dict[str, int]]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkEydWczbUIxRFQiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiI0MzYyMjYzIiwidXNlcl9ndWlkIjoiNjU3MzQ4NjUtMzQ5Yy00ZGE2LTllNmQtZmE5MzVmYWIwZjNkIiwidG9rZW5faWQiOiIwIiwiYXBwX2lkIjoiMjEiLCJpc19ndWVzdCI6dHJ1ZSwibmJmIjoxNzkxMTc2NzAwLCJleHAiOjE3OTEyNjY3MDAsImlhdCI6MTc5MTE4MDMwMCwiaXNzIjoiaHR0cHM6Ly93d3cuY21vbmV5LnR3IiwiYXVkIjoiY21vbmV5YXBpIn0.VUyIH8B-aa66vaS3vKBUYDLq7uvbQW3tIkge_KuK5I1SnOr61js_yhkEL7A61y4FW8akvSODA0jtRsOR1638j3tkIP7-Q7npb4xh5PrLLmjaHfBmp_BayUXjx7m0XV7HY9uvHaB2cveY1igyIn2cqVhHSLN3uAj0H7S8obNaiusagiPXPx5Odn5fRKGLslN0FIWizoj7uZg6af9oV2d6WL9Ig9VEgRftaxbaMci0OwFjptwY8IvZzuu_-27UidyYfLVhYZl19wtGKFhBNEyx9zkHUijzhhGdHzDGxQ7-Ljx9veUcrrWu15ecAVCwzD9bsKPNDgjVigPwx0wdkwNy6A",
        "referer": f"https://www.cmoney.tw/forum/stock/{code}",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
        "x-version": "3.0",
    }
    params = {
        "limit": 20,
    }

    url = f"https://www.cmoney.tw/api/mach/api/Article/Stocks/{code}/AllLatest"

    return url, headers, params


def get_parse_data(response: Response) -> dict[str, dict]:
    print(
        f"取得 {response.url} 資料，狀態碼: {response.status_code}，格式: {response.headers.get('content-type')}"
    )

    if response.headers.get("content-type") == "application/json; charset=utf-8":
        data = response.json()
        record = parse_json_post_field(articles=data.get("articles", []))

    return record


def get_cmoney_monthly_records(code: str, month: int, cursor: str) -> dict[dict[str, dict]]:

    records = {}
    url, headers, params = get_parameter(code=code)

    while True:
        if not cursor:
            return records

        params["cursor"] = cursor
        response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
        record = get_parse_data(response=response)

        if not record:
            return records

        for data in record.values():
            created_time = data.get("create_time")
            target_date = datetime(2026, month, 1, 0, 0)


            if created_time > target_date:
                print(f"created_time: {created_time}, target_date: {target_date}")
                records.update(record)
            else:
                return records
    
        cursor = response.json().get("nextCursor")


def main(code: str = "2317"):

    records = {}
    cursors = get_yearly_cursors(year=2026)
    cursors = cursors[::-1]
    
    for index in range(len(cursors) - 1):
        print(
            f"正在取得 {code} 股票，{2026} 年 {len(cursors) - (index + 1)} 月的文章資料，cursor 為 {cursors[index]}"
        )
        records.update(
            get_cmoney_monthly_records(
                code=code, month=len(cursors) - (index + 1), cursor=cursors[index]
            )
        )
        print("#" * 50)

    print(f"已取得 {code} 股票，{2026} 年的文章資料，總共 {len(records)} 筆")
    export_csv(code=code, records=records)


if __name__ == "__main__":
    import time

    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    start_time = time.perf_counter()
    main(code="6214")
    end_time = time.perf_counter()
    elapsed_time = time.perf_counter() - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    print(f"總共所花費時間為 {int(minutes)} 分 {seconds:.2f} 秒")
