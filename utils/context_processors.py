import time
from datetime import timedelta
from urllib.parse import urlencode
from django.utils import timezone
from sitesetting.models import SiteSetting


NOINDEX_PATH_PREFIXES = (
    "/user/",
    "/dashboard/",
    "/order/",
    "/cart/",
    "/checkout/",
    "/account/",
    "/store-panel/",
    "/admin-panel/",
    "/admin/",
    "/guarantee/active-search/",
)

NOINDEX_QUERY_PARAMS = {
    "search",
    "q",
    "sort",
    "order_by",
    "start_price",
    "end_price",
    "available",
    "store",
    "tag",
    "date",
    "page",
}


def ckeditor_config(request):
    return {"ckeditor_config": "mobile" if request.user_agent.is_mobile else "default"}


def timestamp(request):
    return {"ts": int(time.time())}


def get_sitesetting(request):
    scheme = "https" if request.is_secure() else request.scheme
    host = request.get_host()
    site_url = f"{scheme}://{host}"
    path = request.path

    # Determine canonical URL (strip tracking, sorting, cache-busters, and filter params)
    # Preserve clean single-category or single-brand landing pages on /product/ or /blog/
    canonical_query = {}
    params = request.GET
    is_noindex = any(path.startswith(prefix) for prefix in NOINDEX_PATH_PREFIXES)

    if not is_noindex and params:
        param_keys = {k for k, v in params.items() if v.strip()}
        meaningful_keys = param_keys - {"_", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"}

        if meaningful_keys & NOINDEX_QUERY_PARAMS:
            is_noindex = True
        elif path in ("/product/", "/blog/"):
            cat_vals = [v.strip() for v in params.getlist("category") if v.strip().isdigit()]
            brand_vals = [v.strip() for v in params.getlist("brand") if v.strip().isdigit()]
            if meaningful_keys == {"category"} and len(cat_vals) == 1:
                canonical_query = {"category": cat_vals[0]}
            elif path == "/product/" and meaningful_keys == {"brand"} and len(brand_vals) == 1:
                canonical_query = {"brand": brand_vals[0]}
            elif meaningful_keys:
                is_noindex = True

    canonical_url = f"{site_url}{path}"
    if canonical_query:
        canonical_url = f"{canonical_url}?{urlencode(canonical_query)}"

    return {
        "site": request.site,
        "site_url": site_url,
        "canonical_url": canonical_url,
        "seo_robots": "noindex, follow" if is_noindex else "index, follow",
        "price_valid_until": (timezone.now().date() + timedelta(days=30)).isoformat(),
    }
