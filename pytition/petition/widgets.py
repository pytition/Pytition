from django import forms

class SwitchWidget(forms.CheckboxInput):
    template_name = "petition/widgets/SwitchInput.html"

    def get_context(self, name, value, attrs):
        if attrs == None:
            attrs = {}
        if 'class' in attrs:
            attrs['class'] = attrs['class'] + " custom-control-input"
        else:
            attrs.update({'class': 'custom-control-input'})

        ctx = super(SwitchWidget, self).get_context(name, value, attrs)
        ctx['widget'].update({'label': self.label})
        return ctx

    def __init__(self, *args, **kwargs):
        super(SwitchWidget, self).__init__(*args, **kwargs)
        if 'label' in kwargs:
            self.label = kwargs.pop('label')

class SwitchField(forms.BooleanField):
    widget = SwitchWidget

    def __init__(self, *args, **kwargs):
        super(SwitchField, self).__init__(*args, **kwargs)
        if 'label' in kwargs:
            self.widget.label = kwargs['label']

    def get_bound_field(self, form, field_name):
        bf = super(SwitchField, self).get_bound_field(form, field_name)
        bf.label_tag = self.label_tag
        return bf

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        return ""