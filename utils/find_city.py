import json
from pathlib import Path

try:
    from combined_with_prompt import CITIES_DATA
except Exception as e:
    from .combined_with_prompt import CITIES_DATA


def convert_json_to_dict(json_file_path: str = "combined_with_prompt.json",
                         output_file_path: str = "combined_with_prompt.py"):
    """
    تبدیل فایل JSON به دیکشنری پایتون با ساختار دو سطحی {province: {city: data}}
    و ذخیره در فایل .py

    Args:
        json_file_path: مسیر فایل JSON ورودی
        output_file_path: مسیر فایل پایتون خروجی
    """
    # لود فایل JSON
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"خطا: فایل {json_file_path} پیدا نشد!")
        return
    except json.JSONDecodeError:
        print(f"خطا: فایل {json_file_path} ساختار JSON درستی ندارد!")
        return

    city_dict = {}
    for entry in data:
        city = entry.get('title', '').strip().lower()
        province = entry.get('stateTitle', '').strip().lower()

        if province not in city_dict:
            city_dict[province] = {}

        city_dict[province][city] = {
            'title': entry.get('title', ''),
            'stateTitle': entry.get('stateTitle', ''),
            'tipax_id': entry.get('tipax_id'),
            'post_id': entry.get('post_id')
        }

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("# Auto-generated Python dictionary from combined_with_prompt.json\n")
            f.write("CITIES_DATA = ")
            json.dump(city_dict, f, ensure_ascii=False, indent=4)
            f.write("\n")
        print(f"فایل {output_file_path} با موفقیت ساخته شد!")
    except Exception as e:
        print(f"خطا در نوشتن فایل {output_file_path}: {str(e)}")


def search_city(province: str, city: str, fuzzy_threshold: int = 80):


    """
    سرچ شهر در استان با پشتیبانی از سرچ دقیق و فازی

    Args:
        province: نام استان
        city: نام شهر
        fuzzy_threshold: آستانه امتیاز برای سرچ فازی (0-100)

    Returns:
        دیکشنری اطلاعات شهر اگر پیدا شد، وگرنه None
    """

    from rapidfuzz import fuzz, process

    province = province.strip().lower()
    city = city.strip().lower()

    if province in CITIES_DATA:
        province_key = province
    else:
        province_match = process.extractOne(
            province, CITIES_DATA.keys(), scorer=fuzz.token_sort_ratio, score_cutoff=fuzzy_threshold
        )
        if not province_match:
            return 0, 'استان مورد نظر پیدا نشد'

        return 0,  f'نتایج جستجوی نام استان پیدا شده : "{province_match[0]}" در صورت درست بودن نام دقیق استان را وارد کنید'


    if city in CITIES_DATA[province_key]:
        return 1,CITIES_DATA[province_key][city]

    city_match = process.extractOne(
        city, CITIES_DATA[province_key].keys(), scorer=fuzz.token_sort_ratio, score_cutoff=fuzzy_threshold
    )
    if city_match:
        return 0,  f'نتایج جستجوی نام شهر وارد شده  "{CITIES_DATA[province_key][city_match[0]]['title']}" در صورت درست بودن جستجو نام ان را به صورت دقیق وارد کنید'


    return 0, 'شهر مورد نظر بافت نشد'


