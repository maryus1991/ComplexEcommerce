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


def reformat_city_names():
    import difflib
    from pprint import pprint
    data = CITIES_DATA
    cities = []
    for province, city_map in CITIES_DATA.items():
        for city_name, info in city_map.items():
            cities.append({
                "province": province,
                "city_key": city_name,
                "title": info["title"],
                "stateTitle": info["stateTitle"],
                "tipax_id": info["tipax_id"],
                "post_id": info["post_id"]
            })

    checked = set()


    for i in range(len(cities)):
        city1 = cities[i]
        for j in range(i + 1, len(cities)):
            city2 = cities[j]

            # فقط شهرهای داخل یه استان رو مقایسه کن
            if city1["province"] != city2["province"]:
                continue

            key1 = city1["city_key"]
            key2 = city2["city_key"]

            pair_id = tuple(sorted([key1, key2]))
            if pair_id in checked:
                continue

            checked.add(pair_id)

            # تشخیص شباهت
            ratio = difflib.SequenceMatcher(None, key1, key2).ratio()
            if ratio >= 0.7:  # آستانه شباهت
                print(f"\n❓ آیا این دو شهر یکی هستن؟")
                print(f"  🟦 {key1}   ⇔   🟩 {key2}")
                print(f"    tipax/post: {city1['tipax_id']}/{city1['post_id']} ⇔ {city2['tipax_id']}/{city2['post_id']}")

                confirm = input("اگر یکی هستن بنویس y (بقیه چیزها رو رد می‌کنه): ").strip().lower()
                if confirm == "y":
                    # مرج در دیکشنری اصلی
                    main_city = data[city1["province"]][key1]
                    other_city = data[city2["province"]][key2]

                    if main_city["tipax_id"] is None and other_city["tipax_id"] is not None:
                        main_city["tipax_id"] = other_city["tipax_id"]

                    if main_city["post_id"] is None and other_city["post_id"] is not None:
                        main_city["post_id"] = other_city["post_id"]

                    print("✅ مرج انجام شد. حالا حذف شهر دوم؟ (y/n)")
                    if input().strip().lower() == "y":
                        del data[city2["province"]][key2]
                        print("🗑️ شهر دوم حذف شد.")

    print("\n🎉 پردازش تمام شد.")

    with open("merged_output.py", "w", encoding="utf-8") as f:
        f.write("data = ")
        f.write(repr(data))
