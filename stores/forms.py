from django import forms

from django.core.validators import (FileExtensionValidator,
                                    ValidationError,
                                    validate_email)
from django.contrib.auth.password_validation import validate_password

from dashboard.models import Ticket, TicketConversation
from multiupload.fields import MultiUploadMetaInput
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.validators import validate_phonenumber
from product.models import Product, ProductCategory, ProductBrand
from ckeditor_uploader.fields import RichTextUploadingFormField
from blog.models import Blog, BlogCategory
from .models import Store, StoreApps
from .upload_multi_image import MultiImageField
from user.models import User

from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

from django import forms

class TicketFilterForm(forms.Form):
    subject = forms.CharField(
        label="جستوجو",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )

    store_name = forms.CharField(
        label="نام فروشگاه",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )

    user_name = forms.CharField(
        label="نام کاربر",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )

    user_number = PhoneNumberField(
        label="شماره کاربر",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'dir':'rtl'
        })
    )

    start_date = JalaliDateField(
        label='از تاریخ '
        ,widget=AdminJalaliDateWidget(
            attrs={
                'class' : 'form-control',
                'dir':'rtl'
            }
        )
    )
    end_date = JalaliDateField(
        label='تا تاریخ'
        ,widget=AdminJalaliDateWidget(
            attrs={
                'class' : 'form-control',
                'dir':'rtl'
            }
        )
    )

    ticket_status =  forms.ChoiceField(
        label='وضعیت',
        choices=[
            ('', '-- انتخاب --'),
            ('11', 'بسته'),
            ('12', 'باز'),
            ('12', 'خوانده نشده '),
            ('12', 'خوانده شده'),
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )
    ticket_status_read_in_responder =  forms.ChoiceField(
        label='وضعیت در دریافت کننده',
        choices=[
            ('', '-- انتخاب --'),
            ('11', 'خوانده شده توسط دریافت کننده'),
            ('12', 'خوانده نشده توسط دریافت کننده'),

        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    ordering =  forms.ChoiceField(
        label='ترتیب بندی ',
        choices=[
            ('', '-- انتخاب --'),

            ('12', 'جدیدترین '),
            ('12', 'قدیمی ترین'),
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )



class ProductSearchForm(forms.Form):
    name = forms.CharField(label='جستجوی محصول', required=False,
                           widget=forms.TextInput(
                               attrs={
                                   'class': 'form-control'
                               }
                           )
                           )
    have_discount = forms.ChoiceField(
        label='دارای تخفیف',
        choices=[('', '-- انتخاب --'), ('1', 'بله'), ('0', 'خیر')],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    ordering = forms.ChoiceField(
        label='ترتیب بندی بر اساس',
        choices=[
            ('', '-- انتخاب --'),
            ('11', 'بیشترین بازدید'),
            ('12', 'کمترین بازدید'),
            ('21', 'بیشترین قیمت'),
            ('22', 'کمترین قیمت'),
            ('31', 'بیشترین تعداد کامنت'),
            ('32', 'کمترین  تعداد کامنت'),
            ('41', 'بیشترین موجودی کالا'),
            ('42', 'کمترین موجودی کالا'),
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    is_active = forms.ChoiceField(
        label='فعال / غیرفعال',
        choices=[('', '-- انتخاب --'), ('1', 'فعال'), ('0', 'غیرفعال')],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )
    discount_min = forms.IntegerField(label='حداقل تخفیف', required=False,
                                      widget=forms.NumberInput(
                                          attrs={
                                              'class': 'form-control'
                                          }
                                      ))
    discount_max = forms.IntegerField(label='حداکثر تخفیف', required=False,
                                      widget=forms.NumberInput(
                                          attrs={
                                              'class': 'form-control'
                                          }
                                      ))
    category = forms.ModelChoiceField(queryset=ProductCategory.objects.filter(is_active=True).all(),
                                      label='دسته‌بندی', required=False,
                                      widget=forms.Select(
                                          attrs={
                                              'class': 'form-control select2 select2-hidden-accessible"',
                                              'style': "width: 100%;",
                                              'tabindex ': "-1",
                                              'aria - hidden ': "true",
                                          }
                                      )
                                      )
    brand = forms.ModelChoiceField(queryset=ProductBrand.objects.filter(is_active=True).all(),
                                   label='برند', required=False,
                                   widget=forms.Select(
                                       attrs={
                                           'class': 'form-control select2 select2-hidden-accessible"',
                                           'style': "width: 100%;",
                                           'tabindex ': "-1",
                                           'aria - hidden ': "true",
                                       }
                                   )
                                   )
    count_min = forms.IntegerField(label='حداقل تعداد', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    count_max = forms.IntegerField(label='حداکثر تعداد', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    weight_min = forms.IntegerField(label='حداقل وزن', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    weight_max = forms.IntegerField(label='حداکثر وزن', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    price_min = forms.IntegerField(label='حداقل قیمت', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    price_max = forms.IntegerField(label='حداکثر قیمت', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    height_min = forms.IntegerField(label='حداقل ارتفاع', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    height_max = forms.IntegerField(label='حداکثر ارتفاع', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    length_min = forms.IntegerField(label='حداقل طول', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    length_max = forms.IntegerField(label='حداکثر طول', required=False,
                                    widget=forms.NumberInput(
                                        attrs={
                                            'class': 'form-control'
                                        }
                                    ))
    width_min = forms.IntegerField(label='حداقل عرض', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    width_max = forms.IntegerField(label='حداکثر عرض', required=False,
                                   widget=forms.NumberInput(
                                       attrs={
                                           'class': 'form-control'
                                       }
                                   ))
    feature = forms.CharField(label='جستجو در ویژگی‌ها', required=False,
                              widget=forms.TextInput(
                                  attrs={
                                      'class': 'form-control',
                                      'placeholder': 'ایتم های مورد نظر را بنویسید و با - از هم جدا کنید'
                                  }
                              )
                              )
    tag = forms.CharField(label='جستجو در تگ‌ها', required=False,
                          widget=forms.TextInput(
                              attrs={
                                  'class': 'form-control',
                                  'placeholder': 'ایتم های مورد نظر را بنویسید و با - از هم جدا کنید'
                              }
                          )
                          )

    def clean(self):
        items = self.cleaned_data
        # Create a list of keys to remove first
        keys_to_remove = [key for key, value in items.items()
                          if value is None or value == '']
        # Then remove them
        for key in keys_to_remove:
            items.pop(key)
        return items

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if name is not None and name != '':
            return name
        else:
            return None


class BrandAndCategorySearchForm(forms.Form):
    name = forms.CharField(
        label='جستجوی',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    is_active = forms.ChoiceField(
        label='فعال / غیرفعال',
        choices=[
            ('', '-- انتخاب --'),
            ('1', 'فعال'),
            ('0', 'غیرفعال')
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )
    ordering = forms.ChoiceField(
        label='ترتیب بندی بر اساس',
        choices=[
            ('', '-- انتخاب --'),
            ('41', 'بیشترین تعداد کالا'),
            ('42', 'کمترین تعداد کالا'),
            ('51', 'جدید ترین'),
            ('52', 'قدیمی ترین'),
        ],
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        ),
    )

    category_parent = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(),
        label='دسته‌بندی مادر   ', required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible"',
                'style': "width: 100%;",
                'tabindex ': "-1",
                'aria - hidden ': "true",
            }
        )
    )

    def clean(self):
        items = self.cleaned_data
        # Create a list of keys to remove first
        keys_to_remove = [key for key, value in items.items()
                          if value is None or value == '']
        # Then remove them
        for key in keys_to_remove:
            items.pop(key)
        return items


class AddProductForm(forms.ModelForm):
    description = RichTextUploadingFormField()
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).all(), required=True,
        empty_label='دسته بندی مربوطه را انتخاب کنید',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible"',
                'style': "width: 100%;",
                'tabindex ': "-1",
                'aria - hidden ': "true",
                'placeholder': 'درسته بندی'

            }
        ))
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).all(), required=True,
        empty_label='برند مربوطه را انتخاب کنید',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible"',
                'style': "width: 100%;",
                'tabindex ': "-1",
                'aria - hidden ': "true",
                'placeholder': 'برند'

            }
        ))

    picture = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تصویر اصلی'

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]

    )

    gallery = MultiImageField(
        required=True,
        max_num=10,
        min_num=0,
        widget=MultiUploadMetaInput(
            attrs={
                'class': 'form-control',

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]

    )

    have_discount = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={

                'type': "checkbox",

            }
        )
    )

    features = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'ویژگی های محصول را اضافه کنید ... ',
                'id': 'id_features'
            }
        )
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تگ های محصول را اضافه کنید ... ',
                'id': 'id_tags'
            }
        )
    )

    class Meta:
        model = Product
        fields = ('name', 'price', 'description',
                  'category', 'have_discount', 'discount',
                  'picture', 'brand', 'count',
                  'weight', 'tags', 'features', 'gallery',
                  'length', 'width', 'height',
                  )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'قیمت'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ارتفاع'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'طول'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عرض'
            }),

            'discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'تخفیف',
                'value': 0

            }, ),
            'count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'تعداد'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'وزن (گرم)'
            }),
        }


class AddBrandForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={

                'placeholder': 'تصویر لوگو'

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ])

    class Meta:
        model = ProductBrand
        fields = ('name', 'image', 'is_active',)
        widgets = {
            'name': forms.TextInput(attrs={

                'class': 'form-control',
            }),

            'is_active': forms.CheckboxInput(
                attrs={

                    'checked': 'checked'
                }
            )

        }


class AddCategoryForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(
            is_active=True).all(), required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible"',
                'style': "width: 100%;",
                'tabindex ': "-1",
                'aria - hidden ': "true",

            }
        ), empty_label='دسته مادر یا دسته بالا دست را انتخاب کنید'
    )

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={

                'placeholder': 'تصویر لوگو'

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ])

    class Meta:
        model = ProductCategory
        fields = ('name', 'is_active', 'image', 'parent')
        widgets = {
            'name': forms.TextInput(attrs={

                'class': 'form-control',
            }),

            'is_active': forms.CheckboxInput(
                attrs={

                    'checked': 'checked'
                }
            )
        }


class AddStoreForm(forms.ModelForm):
    logo = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'لوگو'

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )
    about_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تصویر معرفی'

            }
        ),
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'heic'])
        ]
    )

    phone = PhoneNumberField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'شماره همراه'
            }
        ), required=True,
        validators=[validate_phonenumber]
    )

    phone2 = PhoneNumberField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'شماره تلفن ثابت'
            }
        ), required=True,
        validators=[validate_phonenumber]
    )

    merchant_id = forms.CharField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'مرچنت کد زرین پال'
            }
        )
    )

    class Meta:
        model = Store

        fields = ('name', 'phone', 'phone2',
                  'whats_app_ID', 'whats_app_link',
                  'telegram_app_ID', 'telegram_app_Link',
                  'instagram_app_ID', 'instagram_app_Link',
                  'merchant_id', 'logo', 'address', 'about_image',
                  'orgin_city_id', 'is_active',
                  )

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام فروشگاه',
            }),
            'whats_app_link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'لینک واتساپ',
                    'type': 'text'
                }
            ),
            'whats_app_ID': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ای دی واتساپ'
                }
            ),
            'telegram_app_ID': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ای دی تلگرام'
                }
            ),
            'telegram_app_Link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'لینک تلگرام',
                    'type': 'text'
                }
            ),
            'instagram_app_ID': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ای دی اینستاگرام'
                }
            ),
            'instagram_app_Link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'لینک اینستاگرام',
                    'type': 'text'
                }
            ),

            'address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ادرس فرشگاه'
                }
            ),
            'orgin_city_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': ' شهر مبدا'
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={

                }
            ),
        }


class StoreSendTicketForm(forms.ModelForm):
    store = forms.ModelChoiceField(
        required=False,
        queryset=Store.objects.filter(is_active=True,
                                      is_verified=True).all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible',
                'style': "width: 100%",
                'aria - hidden': "true",
                'tabindex': "-1",
                'dir':'rtl'
            }
        ), empty_label='لطفا فروشگاهی که می خوایید تیکت به ان ارسال شود را انتخاب کنید'
    )
    message_message = RichTextUploadingFormField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'متن تیکت ...'
            }
        ), config_name='default'
    )

    class Meta:
        model = Ticket
        fields = (
            'subject',
            'store',
            'message_message',
        )
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان را وارد کنید ... '
            })
        }


class AddStoreUserStaffForm(forms.ModelForm):
    """
    for create user staff for stores
    """

    class Meta:
        model = User
        fields = (
            'email', 'PhoneNumber', 'first_name', 'last_name', 'password', 'is_store_admin'
        )

    is_store_admin = forms.BooleanField(
        required=False
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل ...',
                'autocomplete': "email"

            }
        )
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'نام ...'
            }
        )
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی ...'
            }
        )
    )
    PhoneNumber = PhoneNumberField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': "شماره همراه",
            'autocomplete': "tel",
            'dir': 'rtl'

        })
    )

    password = forms.CharField(required=False,
                               widget=forms.PasswordInput(
                                   attrs={
                                       'class': 'form-control',
                                       'placeholder': "رمز عبور",
                                       'autocomplete': "password"
                                   }
                               ))

    conform_password = forms.CharField(required=False,
                                       widget=forms.PasswordInput(
                                           attrs={
                                               'class': 'form-control',
                                               'placeholder': "تایید رمز عبور",
                                           }
                                       ))

    def clean_conform_password(self):
        conform_password = self.cleaned_data['conform_password']
        password = self.cleaned_data.get('password')

        if password and conform_password:

            if password != conform_password:
                raise ValidationError(
                    'رمز عبور شما به صورت یکسان وارد نشده است'
                )
            else:
                return conform_password

        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data['password']
        if password:
            validate_password(password)
        return password

    def clean_email(self):
        email = self.cleaned_data['email']
        validate_email(email)
        return email

    def clean_phone_number(self):
        PhoneNumber = self.cleaned_data['PhoneNumber']
        validate_phonenumber(PhoneNumber)

        return PhoneNumber


class AddStoreAppForm(forms.ModelForm):
    """
    for upload apps for stores
    """

    class Meta:
        model = StoreApps
        fields = (
            'is_active', 'name', 'file'
        )
        widgets = {
            'is_active': forms.CheckboxInput()
            , 'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام را وارد کنید'
            })
            , 'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': "برنامه را وارد کنید"
            })
        }


class AddStoreBlogForm(forms.ModelForm):
    """
    for add blogs for stores
    """
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تصویر '

            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'jpg', 'jpeg', 'png', 'webp', 'heic'
                ]
            )
        ]

    )
    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible',
                'style': "width: 100%;",
                'tabindex': "-1",
                'aria - hidden': "true"
            }
        )
        , empty_label='لطفا دسته بندی انتخاب کنید'
    )
    content = RichTextUploadingFormField()

    class Meta:
        model = Blog
        fields = ('title', 'category', 'content', 'image')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان را وارد کنید'
            })
        }


class AddStoreBlogCategoryForm(forms.ModelForm):
    """
    for add blogs categories for stores
    """

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تصویر '

            }
        ),
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'jpg', 'jpeg', 'png', 'webp', 'heic'
                ]
            )
        ]

    )

    parent = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control select2 select2-hidden-accessible',
                'style': "width: 100%;",
                'tabindex': "-1",
                'aria - hidden': "true"
            }
        )
        , empty_label='لطفا دسته بندی مادر انتخاب کنید',
        required=False
    )

    class Meta:
        model = BlogCategory
        fields = ('name', 'parent', 'image',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام دسته را وارد کنید'
            }),

        }
