# utils/downloader.py
import os
import requests
from config import HEADERS, ENABLE_IMAGE_DOWNLOAD, ENABLE_DEBUG_LOGS

def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def download_image(image_url, save_path, timeout=20):
    """
    دانلود تصویر. اگر ENABLE_IMAGE_DOWNLOAD==False فقط True برمی‌گرداند و فایل دانلود نمی‌شود.
    در صورت خطا False برمی‌گرداند.
    """
    if not image_url:
        return False
    if not ENABLE_IMAGE_DOWNLOAD:
        # اگر دانلود غیرفعال است، فقط بعنوان "موفق" تلقی می‌کنیم (تا مسیر در خروجی قرار بگیرد).
        return True
    try:
        clean = str(image_url).split('?')[0]
        r = requests.get(clean, headers=HEADERS, stream=True, timeout=timeout)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"      ✖ خطا در دانلود تصویر ({image_url}): {e}")
        return False

def save_debug_json(obj, filepath):
    """ذخیره JSON دیباگ در صورت فعال بودن ENABLE_DEBUG_LOGS"""
    # این تابع هیچ کنترلی روی ENABLE_DEBUG_LOGS ندارد — caller تصمیم می‌گیرد ذخیره کند یا نه.
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            import json
            json.dump(obj, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"      ⚠️ خطا در ذخیره دیباگ: {e}")
        return False
