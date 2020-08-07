import re

from django.utils.safestring import mark_safe
from djaveForm.form_element import FormElement


BUTTON_SPACER = '<div style="button_spacer"></div>'


class Button(FormElement):
  def __init__(
      self, text, key_prefix=None, pk=None, button_type='button',
      css_class=None, additional_attrs=None):
    key_prefix = key_prefix or re.compile(r'[^\w]').sub('', text).lower()
    super().__init__(key_prefix, pk, additional_attrs=additional_attrs)
    self.text = text
    self.button_type = button_type
    self.css_class = css_class or key_prefix

    self._was_clicked = None
    self._was_clicked_set = False

  def set_was_clicked(self, was_clicked):
    self._was_clicked = was_clicked
    self._was_clicked_set = True

  def get_was_clicked(self, post_data=None):
    if post_data is not None:
      return self.key() in post_data
    if not self._was_clicked_set:
      raise Exception(
          'I can not tell you if this button was clicked because '
          'set_was_clicked was never called and you didnt pass in post_data. '
          'You may need to call set_form_data on the form containing '
          'this button, or you may need to check that this button is actually '
          'added to the form controls.')
    return self._was_clicked

  def as_csv(self):
    return ''

  def as_html(self):
    use_css_class = self.css_class or self.key_prefix or ''
    css_class_str = ''
    if use_css_class:
      css_class_str = ' class="{}"'.format(use_css_class)
    name_attr = ''
    if self.key():
      name_attr = ' name="{}" value="{}"'.format(self.key(), self.key())
    return mark_safe((
        '<button type="{}"{}{}{}>'
        '{}</button>').format(
            self.button_type, css_class_str, name_attr,
            self.additional_attrs_str(), self.text))
