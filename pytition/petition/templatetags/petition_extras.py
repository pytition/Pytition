from django import template
from petition.helpers import sanitize_html

register = template.Library()


from widget_tweaks.templatetags.widget_tweaks import add_class

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

@register.filter
def getitem(array, item):
    """
    Get an item from an item.

    Args:
        array: (array): write your description
        item: (str): write your description
    """
    return array[item]

@register.filter
def bootstrap(field):
    """
    Returns an instance of widget.

    Args:
        field: (todo): write your description
    """
    if hasattr(field, 'field') and hasattr(field.field, 'widget') and field.field.widget:
        widget = field.field.widget.__class__.__name__.lower()
        if widget in ["passwordinput", "textinput", "textarea", "select", "numberinput", "emailinput"]:
            return add_class(field, "form-control")
        if widget in ["checkboxinput", "radioselect"]:
            return add_class(field, "form-check-input")
        if widget == "fileinput":
            return add_class(field, "form-control-file")
    return field

@register.filter
def html_sanitize(html):
    """
    Sanitize an html.

    Args:
        html: (str): write your description
    """
    return sanitize_html(html)