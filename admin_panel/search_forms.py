from product.models import ProductCategory, ProductBrand
from stores.models import Store
from django import forms





class ProductSearchForm(forms.Form):
    name = forms.CharField(
        label="جستجوی محصول",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    have_discount = forms.ChoiceField(
        label="دارای تخفیف",
        choices=[("", "-- انتخاب --"), ("1", "بله"), ("0", "خیر")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    ordering = forms.ChoiceField(
        label="ترتیب بندی بر اساس",
        choices=[
            ("", "-- انتخاب --"),
            ("19", 'ترتیب انتخابی'),
            ("11", "بیشترین بازدید"),
            ("12", "کمترین بازدید"),
            ("21", "بیشترین قیمت"),
            ("22", "کمترین قیمت"),
            ("31", "بیشترین تعداد کامنت"),
            ("32", "کمترین  تعداد کامنت"),
            ("41", "بیشترین موجودی کالا"),
            ("42", "کمترین موجودی کالا"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    is_active = forms.ChoiceField(
        label="فعال / غیرفعال",
        choices=[("", "-- انتخاب --"), ("1", "فعال"), ("0", "غیرفعال")],
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    admin_verify = forms.ChoiceField(
        label="تایید شده ادمین / تایید نشده ادمین ",
        choices=[("", "-- انتخاب --"), ("1", "تایید شده"), ("0", "تایید نشده")],
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    discount_min = forms.IntegerField(
        label="حداقل تخفیف",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    discount_max = forms.IntegerField(
        label="حداکثر تخفیف",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        label="دسته‌بندی",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        label="فروشگاه",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.all(),
        label="برند",
        required=False,
        widget=forms.Select(
            attrs={
                "class": 'form-control select2 select2-hidden-accessible"',
                "style": "width: 100%;",
                "tabindex ": "-1",
                "aria - hidden ": "true",
            }
        ),
    )
    count_min = forms.IntegerField(
        label="حداقل تعداد",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    count_max = forms.IntegerField(
        label="حداکثر تعداد",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight_min = forms.IntegerField(
        label="حداقل وزن",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight_max = forms.IntegerField(
        label="حداکثر وزن",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_min = forms.IntegerField(
        label="حداقل قیمت",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    price_max = forms.IntegerField(
        label="حداکثر قیمت",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    height_min = forms.IntegerField(
        label="حداقل ارتفاع",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    height_max = forms.IntegerField(
        label="حداکثر ارتفاع",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    length_min = forms.IntegerField(
        label="حداقل طول",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    length_max = forms.IntegerField(
        label="حداکثر طول",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    width_min = forms.IntegerField(
        label="حداقل عرض",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    width_max = forms.IntegerField(
        label="حداکثر عرض",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    feature = forms.CharField(
        label="جستجو در ویژگی‌ها",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایتم های مورد نظر را بنویسید و با - از هم جدا کنید",
            }
        ),
    )
    tag = forms.CharField(
        label="جستجو در تگ‌ها",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایتم های مورد نظر را بنویسید و با - از هم جدا کنید",
            }
        ),
    )

    def clean(self):
        items = self.cleaned_data
        # Create a list of keys to remove first
        keys_to_remove = [
            key for key, value in items.items() if value is None or value == ""
        ]
        # Then remove them
        for key in keys_to_remove:
            items.pop(key)
        return items

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if name is not None and name != "":
            return name
        else:
            return None
