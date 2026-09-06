import contextlib
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from util import logger

RETRIES = Retry(total=3,
                backoff_factor=0.5,
                status_forcelist=[k for k in range(400, 600)])

HOT_URL = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


@contextlib.contextmanager
def request_session():
    s = requests.session()
    try:
        s.mount("http://", HTTPAdapter(max_retries=RETRIES))
        s.mount("https://", HTTPAdapter(max_retries=RETRIES))
        s.headers.update(HEADERS)
        yield s
    finally:
        s.close()


class Toutiao:

    def get_hot_search(self):
        items = []
        resp = None
        try:
            with request_session() as s:
                resp = s.get(HOT_URL)
                obj = resp.json()
                for item in obj.get('data', []):
                    # 转换成旧格式，兼容 main.py 的解析逻辑
                    items.append({
                        'content': json.dumps(
                            {'raw_data': {'title': item['Title']}},
                            ensure_ascii=False)
                    })
        except:
            logger.exception('get hot search failed')
        return (items, resp)


if __name__ == "__main__":
    tt = Toutiao()
    searches, resp = tt.get_hot_search()
    logger.info('searches:%s', searches[0])
