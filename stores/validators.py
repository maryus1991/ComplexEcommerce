import re


def is_valid_message(text: str) -> bool:
    """اعتبارسنجی پیام با پشتیبانی از زبان فارسی"""
    if len(text.strip()) < 2:  # حداقل طول پیام
        return False

    # الگوی regex برای پشتیبانی از فارسی، انگلیسی، اعداد و علائم متداول
    pattern = r"^[\u0600-\u06FF\uFB8A\u067E\u0686\u06AF\u200C\u200Fa-zA-Z0-9\s\.,;:!?\-()،؛؟]+$"
    return bool(re.match(pattern, text))
