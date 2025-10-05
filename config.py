# config.py
# تنظیمات مرکزی اسکریپر — همه گزینه‌ها اینجا کنترل می‌شوند.

# --- تنظیمات اصلی ---
SEARCH_KEYWORD = "خط چشم سالوته"
OUTPUT_NAME = "salute_eyeliner"   # نام پوشه خروجی و فایل
PAGES_TO_SCRAPE = 1               # صفحات جستجو (برای تست =1)

# --- API / networking ---
SEARCH_API_URL = "https://api.digikala.com/v1/search/?q={keyword}&page={page_num}"
PRODUCT_DETAILS_API_URL = "https://api.digikala.com/v2/product/{product_id}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 20  # seconds

# --- قیمت ---
PRICE_DIVISOR = 10  # تبدیل ریال -> تومان (اگر نمی‌خواهی تقسیم بشود، بگذار 1)

# --- قابلیت‌های اختیاری (True/False) ---
ENABLE_GALLERY = False         # اگر False باشد، گالری دانلود و اضافه نمی‌شود
ENABLE_TAGS = False            # اگر False باشد، تگ‌ها نادیده گرفته می‌شوند
ENABLE_DEBUG_LOGS = False     # اگر True فایلهای JSON خامِ debug ذخیره می‌شود
ENABLE_IMAGE_DOWNLOAD = True  # اگر False فقط لینک‌ها در خروجی ثبت می‌شوند (دانلود انجام نمی‌شود)
SAVE_LOG_FILE = False         # اگر True عملیات لاگ هم در output ذخیره می‌شود

# --- جزئیات download / throttling ---
REQUEST_DELAY_RANGE = (1.0, 2.5)   # بین درخواست‌های هر محصول
PAGE_DELAY_RANGE = (2.0, 5.0)      # بین صفحات
MAX_GALLERY_IMAGES = 5             # حداکثر تصاویر گالری دانلودی برای هر محصول

# --- مسیرهای محلی (معمولاً لازم نیست تغییر بدی) ---
OUTPUT_BASE_DIR = "output"
