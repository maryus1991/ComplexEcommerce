from multiupload.fields import MultiUploadMetaField, MEDIA_TYPES
from django import forms
from django.core.exceptions import FieldError
from django.utils.translation import gettext_lazy as _


class CustomMultiUploadField(MultiUploadMetaField):
    """
    for fix validate error in multiupload lib
    """

    def run_validators(self, value):
        value = value or []

        for item in value:
            super().run_validators(item)


class MultiMediaField(CustomMultiUploadField):
    """Handles multimedia files."""

    error_messages = {
        "wrong_type": _("Invalid media_type. Valid types are: %(valid_types)s")
    }

    def __init__(self, *args, **kwargs):
        self.media_type = kwargs.pop("media_type", "image")

        if self.media_type not in MEDIA_TYPES:
            raise FieldError(
                self.error_messages["wrong_type"]
                % {
                    "valid_types": ", ".join(MEDIA_TYPES),
                }
            )

        kwargs.update(
            {
                "attrs": {
                    "accept": "{0}/*".format(self.media_type),
                }
            }
        )
        super().__init__(*args, **kwargs)


class MultiImageField(MultiMediaField, forms.ImageField):
    """Handles multiple image uploads, requires Pillow to be installed."""

    def __init__(self, *args, **kwargs):
        kwargs.update({"media_type": "image"})
        super().__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        for item in data:
            i = forms.ImageField.to_python(self, item)
            if i:
                ret.append(i)
        return ret
