# SPDX-License-Identifier: AGPL-3.0-or-later
"""Baidu_

.. _Baidu: https://www.baidu.com
"""

# There exits a https://github.com/ohblue/baidu-serp-api/
# but we don't use it here (may we can learn from).

from urllib.parse import urlencode
from datetime import datetime
from html import unescape
import time
import json

from searx.exceptions import SearxEngineAPIException, SearxEngineCaptchaException
from searx.utils import html_to_text

about = {
    "website": "https://www.baidu.com",
    "wikidata_id": "Q14772",
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
    "language": "zh",
}

paging = True
categories = []
results_per_page = 10

baidu_category = 'general'

time_range_support = True
time_range_dict = {"day": 86400, "week": 604800, "month": 2592000, "year": 31536000}


def init(_):
    if baidu_category not in ('general', 'images', 'it'):
        raise SearxEngineAPIException(f"Unsupported category: {baidu_category}")


def request(query, params):
    page_num = params["pageno"]

    category_config = {
        'general': {
            'endpoint': 'https://www.baidu.com/s',
            'params': {
                "wd": query,
                "rn": results_per_page,
                "pn": (page_num - 1) * results_per_page,
                "tn": "json",
            },
        },
        'images': {
            'endpoint': 'https://image.baidu.com/search/acjson',
            'params': {
                "word": query,
                "rn": results_per_page,
                "pn": (page_num - 1) * results_per_page,
                "tn": "resultjson_com",
            },
        },
        'it': {
            'endpoint': 'https://kaifa.baidu.com/rest/v1/search',
            'params': {
                "wd": query,
                "pageSize": results_per_page,
                "pageNum": page_num,
                "paramList": f"page_num={page_num},page_size={results_per_page}",
                "position": 0,
            },
        },
    }

    query_params = category_config[baidu_category]['params']
    query_url = category_config[baidu_category]['endpoint']

    if params.get("time_range") in time_range_dict:
        now = int(time.time())
        past = now - time_range_dict[params["time_range"]]

        if baidu_category == 'general':
            query_params["gpc"] = f"stf={past},{now}|stftype=1"

        if baidu_category == 'it':
            query_params["paramList"] += f",timestamp_range={past}-{now}"

    params["url"] = f"{query_url}?{urlencode(query_params)}"
    # 允许重定向，但会在 response 函数中检测验证码重定向
    params["allow_redirects"] = True
    
    # 增强 HTTP 头以更好地模拟真实浏览器，降低被识别为爬虫的概率
    headers = params.get("headers", {})
    # 对于百度搜索，优先接受 JSON，但也接受其他格式（以防万一）
    # 注意：移除 Accept-Encoding 中的 br (Brotli)，因为某些情况下可能导致解码问题
    headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',  # 移除 br，避免可能的解压问题
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': 'https://www.baidu.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'X-Requested-With': 'XMLHttpRequest',
    })
    params["headers"] = headers
    
    return params


def response(resp):
    # 检测响应状态码
    if resp.status_code == 403:
        raise SearxEngineCaptchaException(message='Baidu 403 Forbidden - possible CAPTCHA')
    
    # 检测重定向到验证码页面（检查最终 URL）
    final_url = str(resp.url) if hasattr(resp, 'url') else ''
    if 'wappass.baidu.com/static/captcha' in final_url:
        raise SearxEngineCaptchaException(message='Baidu CAPTCHA detected (redirect to captcha page)')
    
    # 检查响应是否为空
    if not resp.content or len(resp.content) == 0:
        raise SearxEngineAPIException("Baidu returned empty response")
    
    # 尝试多种方式解码响应，处理编码问题
    text = None
    encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    # 首先尝试使用 resp.text（httpx 会自动处理编码和解压）
    try:
        if hasattr(resp, 'text') and resp.text:
            # 检查前几个字符是否是有效的 JSON 或文本
            preview = resp.text[:50].strip()
            if preview and (preview.startswith('{') or preview.startswith('[') or 
                           preview.startswith('<!') or any(c.isprintable() for c in preview)):
                text = resp.text.strip()
    except (UnicodeDecodeError, AttributeError, Exception):
        pass
    
    # 如果 resp.text 失败或返回乱码，尝试手动解码
    if not text:
        for encoding in encodings_to_try:
            try:
                decoded = resp.content.decode(encoding)
                # 检查解码后的内容是否看起来像有效的文本/JSON
                if decoded and len(decoded.strip()) > 0:
                    preview = decoded[:50].strip()
                    if preview.startswith('{') or preview.startswith('[') or preview.startswith('<!'):
                        text = decoded.strip()
                        break
                    # 如果包含可打印字符，也尝试使用
                    if any(c.isprintable() or c.isspace() for c in preview):
                        text = decoded.strip()
                        break
            except (UnicodeDecodeError, UnicodeError):
                continue
    
    # 如果仍然无法解码，使用 UTF-8 并忽略错误
    if not text:
        try:
            text = resp.content.decode('utf-8', errors='ignore').strip()
            # 如果解码后全是乱码字符，可能不是文本
            if text and not any(c.isprintable() or c.isspace() for c in text[:100]):
                raise SearxEngineAPIException("Baidu response appears to be binary data, not text")
        except Exception as e:
            raise SearxEngineAPIException(f"Baidu response cannot be decoded as text: {str(e)}")
    
    if not text or len(text) == 0:
        raise SearxEngineAPIException("Baidu returned empty or unreadable response")
    
    # 检测响应内容中是否包含验证码相关关键词（在解析 JSON 之前）
    if '验证码' in text or 'captcha' in text.lower() or '安全验证' in text:
        # 检查是否是真正的验证码页面，而不是搜索结果中包含这些词
        if 'wappass.baidu.com' in text or 'static/captcha' in text or '<html' in text.lower():
            raise SearxEngineCaptchaException(message='Baidu CAPTCHA detected (in content)')
    
    # 检测是否是 HTML 响应（而不是 JSON）
    if text.startswith('<!DOCTYPE') or text.startswith('<html') or text.startswith('<?xml'):
        # 可能是验证码页面或错误页面
        if '验证码' in text or 'captcha' in text.lower() or '安全验证' in text:
            raise SearxEngineCaptchaException(message='Baidu returned HTML page (likely CAPTCHA)')
        raise SearxEngineAPIException("Baidu returned HTML instead of JSON")
    
    # 尝试解析 JSON
    try:
        if baidu_category == 'images':
            # baidu's JSON encoder wrongly quotes / and ' characters by \\ and \'
            text = text.replace(r"\/", "/").replace(r"\'", "'")
        
        # 检查是否以 JSON 格式开头
        if not (text.startswith('{') or text.startswith('[')):
            # 可能是 HTML 或其他格式，检查是否是验证码
            if '验证码' in text or 'captcha' in text.lower() or '安全验证' in text:
                raise SearxEngineCaptchaException(message='Baidu CAPTCHA detected (non-JSON response)')
            raise SearxEngineAPIException(f"Baidu response is not JSON format. First 200 chars: {text[:200]}")
        
        data = json.loads(text, strict=False)
    except json.JSONDecodeError as e:
        # JSON 解析失败，可能是 HTML 响应或其他格式
        error_msg = f"Failed to parse Baidu JSON response: {str(e)}"
        # 检查是否是验证码页面
        if '验证码' in text or 'captcha' in text.lower() or '安全验证' in text:
            raise SearxEngineCaptchaException(message='Baidu CAPTCHA detected (JSON parse failed)')
        # 显示响应前 500 个字符用于调试
        preview = text[:500] if len(text) > 500 else text
        raise SearxEngineAPIException(f"{error_msg}. Response preview: {preview}")
    
    parsers = {'general': parse_general, 'images': parse_images, 'it': parse_it}

    return parsers[baidu_category](data)


def parse_general(data):
    results = []
    if not data.get("feed", {}).get("entry"):
        raise SearxEngineAPIException("Invalid response")

    for entry in data["feed"]["entry"]:
        if not entry.get("title") or not entry.get("url"):
            continue

        published_date = None
        if entry.get("time"):
            try:
                published_date = datetime.fromtimestamp(entry["time"])
            except (ValueError, TypeError):
                published_date = None

        # title and content sometimes containing characters such as &amp; &#39; &quot; etc...
        title = unescape(entry["title"])
        content = unescape(entry.get("abs", ""))

        results.append(
            {
                "title": title,
                "url": entry["url"],
                "content": content,
                "publishedDate": published_date,
            }
        )
    return results


def parse_images(data):
    results = []
    if "data" in data:
        for item in data["data"]:
            if not item:
                # the last item in the JSON list is empty, the JSON string ends with "}, {}]"
                continue
            replace_url = item.get("replaceUrl", [{}])[0]
            width = item.get("width")
            height = item.get("height")
            img_date = item.get("bdImgnewsDate")
            publishedDate = None
            if img_date:
                publishedDate = datetime.strptime(img_date, "%Y-%m-%d %H:%M")
            results.append(
                {
                    "template": "images.html",
                    "url": replace_url.get("FromURL"),
                    "thumbnail_src": item.get("thumbURL"),
                    "img_src": replace_url.get("ObjURL"),
                    "title": html_to_text(item.get("fromPageTitle")),
                    "source": item.get("fromURLHost"),
                    "resolution": f"{width} x {height}",
                    "img_format": item.get("type"),
                    "filesize": item.get("filesize"),
                    "publishedDate": publishedDate,
                }
            )
    return results


def parse_it(data):
    results = []
    if not data.get("data", {}).get("documents", {}).get("data"):
        raise SearxEngineAPIException("Invalid response")

    for entry in data["data"]["documents"]["data"]:
        results.append(
            {
                'title': entry["techDocDigest"]["title"],
                'url': entry["techDocDigest"]["url"],
                'content': entry["techDocDigest"]["summary"],
            }
        )
    return results
