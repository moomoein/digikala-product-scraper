# utils/parser.py
from config import PRICE_DIVISOR, ENABLE_TAGS, ENABLE_GALLERY, MAX_GALLERY_IMAGES

def _try_keys(obj, keys):
    """کمک: از obj مسیرهای keys را (list) دنبال کن و نتیجه را برگردان."""
    cur = obj
    for key in keys:
        if cur is None:
            return None
        # handle numeric keys for lists
        if isinstance(cur, list) and key.isdigit():
            idx = int(key)
            try:
                cur = cur[idx]
            except (IndexError, TypeError):
                return None
        else:
            try:
                cur = cur[key]
            except Exception:
                return None
    return cur

def find_value_in_cascade(data, paths, default=None):
    """
    تلاش می‌کند مقدار را از لیست مسیرها پیدا کند.
    paths مثال: ['product.price.selling_price', 'default_variant.price.selling_price']
    اگر مسیر بدون 'product.' باشد، خودش یکبار با 'product.' هم امتحان می‌کند.
    """
    if not data:
        return default
    for raw_path in paths:
        if raw_path is None:
            continue
        # try both with and without product. prefix to be tolerant
        candidates = [raw_path]
        if not raw_path.startswith('product.'):
            candidates.insert(0, f'product.{raw_path}')
        for path in candidates:
            keys = path.split('.')
            val = _try_keys(data, keys)
            if val is not None:
                return val
    return default

def extract_price(data, paths, divisor=PRICE_DIVISOR, default=0.0):
    """
    تلاش برای پیدا کردن قیمت در چند مسیر و تبدیل به float (با تقسیم divisor).
    می‌تواند ورودی dict/str/int را هندل کند.
    """
    raw = find_value_in_cascade(data, paths, default=None)
    if raw is None:
        return float(default)

    # اگر dict بود، سعی کن از کلیدهای استاندارد مقدار را استخراج کنی
    if isinstance(raw, dict):
        for k in ('selling_price', 'rrp_price', 'price', 'value', 'amount'):
            if k in raw:
                raw = raw[k]
                break

    try:
        if isinstance(raw, (int, float)):
            num = float(raw)
        else:
            num = float(str(raw).replace(',', '').strip())
    except (ValueError, TypeError):
        return float(default)

    if num <= 0:
        return float(default)
    return round(num / divisor, 2)

def is_variable_product(product_details):
    """تشخیص variable: اگر تعداد واقعی وریانت‌ها > 1 باشد variable است."""
    variants = find_value_in_cascade(product_details, ['product.variants', 'variants'], default=[])
    return isinstance(variants, list) and len(variants) > 1

def get_variants_list(product_details):
    """برگشت لیست variants (همیشه لیست)."""
    v = find_value_in_cascade(product_details, ['product.variants', 'variants'], default=[])
    return v if isinstance(v, list) else []

def build_attributes_from_variants(variants):
    """
    از themes یا attribute های وریانت‌ها attribute list برای ووکامرس بساز.
    خروجی: [{'name':..., 'options':[...], 'position':i, 'visible':True, 'variation':True}, ...]
    """
    attr_map = {}
    for v in variants:
        if not isinstance(v, dict):
            continue
        # themes معمولاً حاوی label و value است
        themes = v.get('themes') or []
        for th in themes:
            label = th.get('label') or th.get('name')
            val_obj = th.get('value')
            if isinstance(val_obj, dict):
                val = val_obj.get('title') or val_obj.get('title_fa') or val_obj.get('code')
            else:
                val = val_obj
            if label and val:
                attr_map.setdefault(label, set()).add(str(val))

    attributes = []
    for i, (k, opts) in enumerate(attr_map.items()):
        attributes.append({
            "name": k,
            "options": sorted(list(opts)),
            "position": i,
            "visible": True,
            "variation": True
        })
    return attributes

def extract_tags(product_details):
    """استخراج تگ‌ها در صورت فعال بودن ENABLE_TAGS."""
    if not ENABLE_TAGS:
        return []
    raw = find_value_in_cascade(product_details, ['product.suggestion_tags', 'suggestion_tags'], default=[])
    tags = []
    if isinstance(raw, list):
        for t in raw:
            if isinstance(t, dict):
                name = t.get('title_fa') or t.get('title') or t.get('name')
                if name:
                    tags.append(str(name))
            elif isinstance(t, str):
                tags.append(t)
    return tags

def pick_main_image_url(product_details):
    """پیدا کردن URL تصویر اصلی از مسیرهای محتمل."""
    candidates = [
        'product.images.main.url.0',
        'product.images.main.url',
        'product.images.list.0.url.0',
        'product.images.list.0.url',
        'product.images.list.0',
        'product.images.list.0.url.0',
        'product.images.0.url.0',
        'product.images.list'
    ]
    val = find_value_in_cascade(product_details, candidates, default=None)
    # val ممکن است لیست یا رشته باشد
    if isinstance(val, list):
        return val[0] if val else None
    return val

def gather_gallery_urls(product_details, max_images=MAX_GALLERY_IMAGES):
    """جمع کردن URLهای گالری (بدون main) — برگشت لیست حداکثر max_images تا."""
    urls = []
    # primary list
    images_list = find_value_in_cascade(product_details, ['product.images.list', 'product.images.list.0'], default=[])
    if isinstance(images_list, list):
        for entry in images_list:
            if isinstance(entry, dict):
                u = entry.get('url')
                if isinstance(u, list) and u:
                    urls.append(u[0])
                elif isinstance(u, str):
                    urls.append(u)
            elif isinstance(entry, str):
                urls.append(entry)
    # remove duplicates and main
    main = pick_main_image_url(product_details)
    filtered = []
    for u in urls:
        if u and u != main and u not in filtered:
            filtered.append(u)
        if len(filtered) >= max_images:
            break
    return filtered[:max_images]
