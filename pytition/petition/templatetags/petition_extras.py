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
    return array[item]

@register.filter
def bootstrap(field):
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
    return sanitize_html(html)