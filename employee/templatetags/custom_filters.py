from django import template
import locale

register = template.Library()

@register.filter
def force_intcomma(value):
    try:
        # 設定本地化為英文，以確保使用逗號作為千分位分隔符
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        # 格式化數字，並移除小數點部分
        formatted_value = locale.format_string("%d", int(value), grouping=True)
        return formatted_value
    except (ValueError, TypeError):
        return value
    finally:
        # 恢復本地化設定，避免影響其他部分
        locale.setlocale(locale.LC_ALL, '')
