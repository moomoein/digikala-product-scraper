# scraper_final.py
import os
import json
import time
import random
from config import *
from utils.fetcher import get_product_ids_from_search, get_product_details
from utils.parser import (
    find_value_in_cascade, extract_price, is_variable_product,
    get_variants_list, build_attributes_from_variants,
    extract_tags, pick_main_image_url, gather_gallery_urls
)
from utils.downloader import ensure_dirs, download_image, save_debug_json

def transform_product(product_details, images_dir, debug_dir=None):
    """
    تبدیل نمایه JSON دریافتی به دیکشنری خروجی ای که قابل ایمپورت / پردازش برای ووکامرس است.
    این تابع همه منطق قیمت/تصویر/attributes/variations را اجرا می‌کند.
    """
    if not product_details:
        return None

    # ذخیره دیباگ (فقط اگر caller خواسته و ENABLE_DEBUG_LOGS=True و debug_dir مشخص باشد)
    product_id = find_value_in_cascade(product_details, ['product.id', 'id'])
    if ENABLE_DEBUG_LOGS and debug_dir:
        ensure_dirs(debug_dir)
        debug_fp = os.path.join(debug_dir, f"debug_product_{product_id}.json")
        save_debug_json(product_details, debug_fp)

    sku = f"DKP-{product_id}" if product_id else None
    if not sku:
        print("      ✖ شناسه محصول یافت نشد؛ نادیده گرفته می‌شود.")
        return None

    name = find_value_in_cascade(product_details, ['product.title_fa', 'product.title_en', 'title'], default='بدون عنوان')
    short_description = name
    # توضیحات HTML
    description = ""
    # از توابع parser می‌توان برای ساخت description استفاده کرد؛
    # برای سادگی، از expert_review و specifications استفاده می‌کنیم:
    expert = find_value_in_cascade(product_details, ['product.expert_reviews.description', 'expert_reviews.description'])
    if expert:
        description += f"<p>{expert}</p>"
    specs = find_value_in_cascade(product_details, ['product.specifications.0.attributes', 'specifications.0.attributes'], default=[])
    if specs:
        description += "<h3>مشخصات فنی</h3><ul>"
        for s in specs:
            if isinstance(s, dict):
                title = s.get('title', 'نامشخص')
                vals = s.get('values', [])
                description += f"<li><strong>{title}:</strong> {', '.join([str(x) for x in vals])}</li>"
        description += "</ul>"

    # تصاویر
    images_out = []
    gallery_out = []

    main_image_url = pick_main_image_url(product_details)
    if main_image_url:
        if ENABLE_IMAGE_DOWNLOAD:
            fn = f"{sku}.jpg"
            fp = os.path.join(images_dir, fn)
            if download_image(main_image_url, fp):
                images_out.append(fn)
            else:
                # fallback: قرار دادن لینک در خروجی اگر دانلود موفق نبود
                images_out.append(main_image_url)
        else:
            images_out.append(main_image_url)
    else:
        # هیچ تصویر اصلی یافت نشد
        pass

    if ENABLE_GALLERY:
        gallery_urls = gather_gallery_urls(product_details)
        for i, url in enumerate(gallery_urls[:MAX_GALLERY_IMAGES]):
            if ENABLE_IMAGE_DOWNLOAD:
                fn = f"{sku}_g{i+1}.jpg"
                fp = os.path.join(images_dir, fn)
                if download_image(url, fp):
                    gallery_out.append(fn)
                else:
                    gallery_out.append(url)
            else:
                gallery_out.append(url)

    # دسته‌بندی
    cat_name = find_value_in_cascade(product_details, ['product.category.title_fa', 'product.category.title', 'category.title_fa', 'category.title'], default=None)
    categories = [{"name": cat_name}] if cat_name else [{"name": SEARCH_KEYWORD}]

    # تگ‌ها
    tags = [{"name": t} for t in extract_tags(product_details)] if ENABLE_TAGS else []

    # وضعیت موجودی (parent) - از default_variant.status یا product.status
    stock_status_parent = "instock" if find_value_in_cascade(product_details, ['product.status', 'default_variant.status', 'variants.0.status']) == 'marketable' else "outofstock"

    # بررسی variable vs simple
    if is_variable_product(product_details):
        # متغیر: attributes از تمام وریانت‌ها و variations ساخته می‌شوند
        variants = get_variants_list(product_details)
        attributes = build_attributes_from_variants(variants)

        variations_out = []
        for v in variants:
            v_id = v.get('id') or v.get('variant_id') or ''
            v_sku = f"{sku}-{v_id}" if v_id else f"{sku}-var"
            v_sale = extract_price(v, ['price.selling_price', 'price'])
            v_rrp = extract_price(v, ['price.rrp_price', 'price'])
            # اگر parent price صفر است (معمولاً) و فقط وریانت قیمت دارد، از وریانت استفاده کن
            if v_rrp <= 0 and v_sale > 0:
                v_rrp = v_sale
            v_sale_final = v_sale if (v_sale > 0 and v_rrp > 0 and v_sale < v_rrp) else 0.0
            v_stock = "instock" if v.get('status') == 'marketable' else "outofstock"

            # attributes per variant
            v_attrs = []
            for th in (v.get('themes') or []):
                nm = th.get('label') or th.get('name')
                val = th.get('value')
                if isinstance(val, dict):
                    val_text = val.get('title') or val.get('title_fa') or val.get('code')
                else:
                    val_text = val
                if nm and val_text:
                    v_attrs.append({"name": nm, "option": str(val_text)})

            # تصویر وریانت
            v_image = None
            img_urls = None
            # بعضی وریانت‌ها ممکن است دارای images باشند
            if isinstance(v, dict):
                img_urls = v.get('images') or v.get('image') or None
            if img_urls:
                # first candidate:
                if isinstance(img_urls, list):
                    candidate = None
                    first = img_urls[0]
                    if isinstance(first, dict):
                        candidate = first.get('url') or (first.get('url', [None])[0] if isinstance(first.get('url'), list) else None)
                    elif isinstance(first, str):
                        candidate = first
                    else:
                        candidate = None
                elif isinstance(img_urls, dict):
                    candidate = img_urls.get('url')
                    if isinstance(candidate, list):
                        candidate = candidate[0] if candidate else None
                else:
                    candidate = img_urls
                if candidate:
                    if ENABLE_IMAGE_DOWNLOAD:
                        vfn = f"{v_sku}.jpg"
                        if download_image(candidate, os.path.join(images_dir, vfn)):
                            v_image = vfn
                        else:
                            v_image = candidate
                    else:
                        v_image = candidate

            variations_out.append({
                "sku": v_sku,
                "parent_sku": sku,
                "regular_price": v_rrp,
                "sale_price": v_sale_final,
                "stock_status": v_stock,
                "attributes": v_attrs,
                "image": v_image
            })

        return {
            "sku": sku,
            "type": "variable",
            "name": name,
            "description": description,
            "short_description": short_description,
            "images": images_out,
            "gallery": gallery_out,
            "categories": categories,
            "tags": tags,
            "attributes": attributes,
            "variations": variations_out
        }

    else:
        # محصول ساده: قیمت‌ها از product.price.* خوانده می‌شوند یا fallback به default_variant/variants[0]
        sale_price = extract_price(product_details, [
            'product.price.selling_price',
            'price.selling_price',
            'default_variant.price.selling_price',
            'variants.0.price.selling_price',
            'product.default_variant.price.selling_price'
        ])
        regular_price = extract_price(product_details, [
            'product.price.rrp_price',
            'price.rrp_price',
            'default_variant.price.rrp_price',
            'variants.0.price.rrp_price',
            'product.default_variant.price.rrp_price'
        ])
        if regular_price <= 0 and sale_price > 0:
            regular_price = sale_price
        sale_price_final = sale_price if (sale_price > 0 and regular_price > 0 and sale_price < regular_price) else 0.0

        return {
            "sku": sku,
            "type": "simple",
            "name": name,
            "description": description,
            "short_description": short_description,
            "regular_price": regular_price,
            "sale_price": sale_price_final,
            "stock_status": stock_status_parent,
            "images": images_out,
            "gallery": gallery_out,
            "categories": categories,
            "tags": tags
        }

def main():
    # آماده‌سازی دایرکتوری‌ها
    output_dir = os.path.join(OUTPUT_BASE_DIR, OUTPUT_NAME)
    images_dir = os.path.join(output_dir, "images")
    debug_dir = os.path.join(output_dir, "debug")
    ensure_dirs(output_dir, images_dir)
    if ENABLE_DEBUG_LOGS:
        ensure_dirs(debug_dir)

    json_filepath = os.path.join(output_dir, f"{OUTPUT_NAME}_products.json")

    total_saved = 0
    with open(json_filepath, 'w', encoding='utf-8') as out_f:
        out_f.write('[\n')
        first_item = True

        for page in range(1, PAGES_TO_SCRAPE + 1):
            print(f"--- گرفتن آی‌دی‌ها از صفحه {page} ---")
            ids = get_product_ids_from_search(SEARCH_KEYWORD, page)
            if not ids:
                print("  ✳️ هیچ آی‌دی‌ای یافت نشد؛ پایان.")
                break

            for i, pid in enumerate(ids):
                print(f"\n[{i+1}/{len(ids)}] پردازش محصول ID: {pid} ...")
                product_json = get_product_details(pid)
                if not product_json:
                    print("    ✖ دریافت جزئیات شکست خورد؛ عبور می‌کنیم.")
                    continue

                transformed = transform_product(product_json, images_dir, debug_dir if ENABLE_DEBUG_LOGS else None)
                if not transformed:
                    print("    ⚠️ تبدیل محصول موفق نبود؛ عبور.")
                    continue

                if not first_item:
                    out_f.write(',\n')
                json.dump(transformed, out_f, ensure_ascii=False, indent=4)
                first_item = False
                total_saved += 1
                print(f"    ✔ محصول '{transformed.get('name')}' ذخیره شد.")

                # تاخیر تصادفی بین درخواست‌ها
                time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

            # تاخیر بین صفحات
            time.sleep(random.uniform(*PAGE_DELAY_RANGE))

        out_f.write('\n]')

    print(f"\n--- پایان عملیات ---\n{total_saved} محصول در فایل '{json_filepath}' ذخیره شد.")
    if ENABLE_IMAGE_DOWNLOAD:
        print(f"تصاویر (یا لینک‌ها) در پوشه '{images_dir}' قرار دارند.")
    if ENABLE_DEBUG_LOGS:
        print(f"فایل‌های دیباگ در پوشه '{debug_dir}' ذخیره شدند.")

if __name__ == "__main__":
    main()
