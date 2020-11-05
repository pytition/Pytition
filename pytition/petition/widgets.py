from django import forms

class SwitchWidget(forms.CheckboxInput):
    template_name = "petition/widgets/SwitchInput.html"

    def get_context(self, name, value, attrs):
        """
        Returns a context to provide the context.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (todo): write your description
            attrs: (dict): write your description
        """
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
        """
        Initialize the label.

        Args:
            self: (todo): write your description
        """
        super(SwitchWidget, self).__init__(*args, **kwargs)
        if 'label' in kwargs:
            self.label = kwargs.pop('label')

class SwitchField(forms.BooleanField):
    widget = SwitchWidget

    def __init__(self, *args, **kwargs):
        """
        Initialize the widget.

        Args:
            self: (todo): write your description
        """
        super(SwitchField, self).__init__(*args, **kwargs)
        if 'label' in kwargs:
            self.widget.label = kwargs['label']

    def get_bound_field(self, form, field_name):
        """
        Returns the form field for this form.

        Args:
            self: (todo): write your description
            form: (todo): write your description
            field_name: (str): write your description
        """
        bf = super(SwitchField, self).get_bound_field(form, field_name)
        bf.label_tag = self.label_tag
        return bf

    def label_tag(self, contents=None, attrs=None, label_suffix=None):
        """
        Return the label for the given tag.

        Args:
            self: (todo): write your description
            contents: (str): write your description
            attrs: (dict): write your description
            label_suffix: (str): write your description
        """
        return ""