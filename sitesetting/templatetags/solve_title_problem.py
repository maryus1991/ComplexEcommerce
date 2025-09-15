from django import template
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def get_block_content(context, block_name):
    try:
        # روش سازگار با تمام نسخه‌های Django
        if not hasattr(context, 'template'):
            return ''

        # پیدا کردن بلاک در نودهای تمپلیت
        def find_block(nodelist, name):
            for node in nodelist:
                if (hasattr(node, 'name') and getattr(node, 'name', None) == name and
                        hasattr(node, 'nodelist')):
                    return node
                if hasattr(node, 'nodelist'):  # برای نودهای مرکب
                    found = find_block(node.nodelist, name)
                    if found:
                        return found
            return None

        block_node = find_block(context.template.nodelist, block_name)
        if block_node:
            with context.push():
                return block_node.nodelist.render(context)
        return ''

    except Exception as e:
        return ''
