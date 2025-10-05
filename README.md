![Python](https://img.shields.io/badge/python-3.8%2B-blue) 
![License](https://img.shields.io/badge/license-MIT-green) 
![Stars](https://img.shields.io/github/stars/moomoein/digikala-product-scraper?style=social)


<img width="100%" height="736" alt="Terminal demo showing the scraper extracting Digikala products" src="https://github.com/user-attachments/assets/e238cf7a-6f4e-474a-8c29-9afbf23f61dc" /> 


# 🧠 Digikala Product Scraper (WooCommerce Ready)

A **professional modular Python scraper** for [Digikala](https://www.digikala.com/) API that extracts all product details — including variants, prices, images, attributes, and categories — into **WooCommerce-ready JSON**.

> 🇮🇷 پشتیبانی کامل از ساختار محصولات دیجی‌کالا (ساده و متغیر)، با تنظیمات قابل سفارشی‌سازی و ساختار ماژولار.

---

## ✨ Features

✅ Supports both **Simple** and **Variable** products  
✅ Extracts **prices**, **variants**, **categories**, **attributes**, **tags**, and **images**  
✅ Configurable via `config.py` — enable/disable gallery, debug logs, or image download  
✅ Saves output as clean, WooCommerce-compatible JSON  
✅ Built with modular structure (`utils/` folder) for reusability and extension  
✅ Supports Persian content natively (UTF-8 output)


---

## 🛠️ Installation

```bash
git clone https://github.com/moomoein/digikala-product-scraper.git
cd digikala-product-scraper
pip install requests
````

---

## ⚙️ Configuration

Edit the `config.py` file:

```python
SEARCH_KEYWORD = "گوشی موبایل"
PAGES_TO_SCRAPE = 2
ENABLE_GALLERY = True
ENABLE_IMAGE_DOWNLOAD = False
ENABLE_DEBUG_LOGS = False
```

---

## 🚀 Usage

```bash
python scraper_final.py
```

Results will be saved in:

```
output/<OUTPUT_NAME>/
    ├── <OUTPUT_NAME>_products.json
    └── images/
```

---

## 📦 Example Output (WooCommerce JSON)

```json
{
  "sku": "DKP-12345",
  "type": "variable",
  "name": "گوشی موبایل سامسونگ مدل Galaxy A54",
  "regular_price": 21500000.0,
  "sale_price": 19800000.0,
  "attributes": [...],
  "variations": [...],
  "categories": [{"name": "موبایل"}]
}
```

---

## 🧩 Folder Structure

```
digikala-product-scraper/
├── config.py          # Configuration & options
├── scraper_final.py   # Main entry point
└── utils/
    ├── fetcher.py     # API requests
    ├── parser.py      # JSON parsing & data extraction
    └── downloader.py  # Image & file handling
```

---

## 🌍 Use Cases

* 🔄 Importing Digikala products into **WooCommerce / WordPress**
* 📊 Competitive product analysis or dataset creation
* 🧠 AI/ML product recommendation training datasets
* 💾 Backup of Digikala product catalogs

---

## 📜 License

MIT License — feel free to use, modify, or contribute.

---

## 🤝 Contribute
Pull requests are welcome!  
If you find this project useful, don't forget to **⭐ Star the repo** and share it with other developers!

## 📬 Contact
Created by [@moomoein](https://github.com/moomoein) — feel free to reach out for collaboration.
