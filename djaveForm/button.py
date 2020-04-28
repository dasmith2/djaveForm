import re

from djaveForm.form_element import FormElement


class Button(FormElement):
  def __init__(
      self, text, key_prefix=None, pk=None, button_type='button',
      css_class=None):
    self.text = text
    self.key_prefix = key_prefix or re.compile(r'[^\w]').sub('', text).lower()
    self.pk = pk
    self.button_type = button_type
    self.css_class = css_class or key_prefix

    self._was_clicked = None
    self._was_clicked_set = False

  def set_was_clicked(self, was_clicked):
    self._was_clicked = was_clicked
    self._was_clicked_set = True

  def get_was_clicked(self):
    if not self._was_clicked_set:
      raise Exception(
          'I can not tell you if this button was clicked because '
          'set_was_clicked was never called.')
    return self._was_clicked

  def as_csv(self):
    return ''

  def as_html(self):
    css_class_str = ''
    if self.css_class:
      css_class_str = ' class="{}"'.format(self.css_class)
    name_attr = ''
    if self.key():
      name_attr = ' name="{}" value="{}"'.format(self.key(), self.key())
    return (
        '<button type="{}"{}{}>'
        '{}</button>').format(
            self.button_type, css_class_str, name_attr, self.text)
