# utils/fetcher.py
import requests
from config import SEARCH_API_URL, PRODUCT_DETAILS_API_URL, HEADERS, REQUEST_TIMEOUT

def get_product_ids_from_search(keyword, page_num):
    """دریافت لیست ID محصولات از API جستجو."""
    try:
        url = SEARCH_API_URL.format(keyword=keyword, page_num=page_num)
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        products = data.get('data', {}).get('products', []) or []
        return [p.get('id') for p in products if p.get('id')]
    except Exception as e:
        print(f"  ✖ خطا در دریافت لیست محصولات (page {page_num}): {e}")
        return []

def get_product_details(product_id):
    """دریافت JSON جزئیات یک محصول (برمی‌گرداند dict یا None)."""
    try:
        url = PRODUCT_DETAILS_API_URL.format(product_id=product_id)
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get('data', {}) if isinstance(data, dict) else {}
    except Exception as e:
        print(f"    ✖ خطا در دریافت جزئیات محصول {product_id}: {e}")
        return None
