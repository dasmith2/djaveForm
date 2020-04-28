from collections import namedtuple
import html

from django.utils.dateparse import parse_date
from djaveForm.form_element import FormElement


class Field(FormElement):
  # You can put djaveForm fields in djaveTables.
  def __init__(
      self, key_prefix, required=False, default=None, pk=None, value=None):
    super().__init__(key_prefix, pk)
    self.required = required
    self.default = default

    self.value = None
    self._value_set = False
    if value is not None and value != '':
      self.set_value(value)

  def set_value(self, value):
    if value == '':
      self.value = None
    else:
      self.value = value
    self._value_set = True

  def explain_why_not_valid(self):
    if self.required and not self.value:
      return 'Required'

  def is_valid(self):
    if not self._value_set:
      raise Exception(
          'If the value of this field was never set, it does not make much '
          'sense to ask if the field is valid.')
    return not self.explain_why_not_valid()

  def as_csv(self):
    if self.value is None:
      return ''
    return str(self.value)

  def as_html(self):
    widget_html = self.widget_html()
    error_html = ''
    if self._value_set:
      why_invalid = self.explain_why_not_valid()
      if why_invalid:
        error_html = '<span class="problem">{}</span>'.format(why_invalid)
    return '{}\n{}'.format(widget_html, error_html)

  def widget_html(self):
    raise NotImplementedError('widget_html')


Option = namedtuple('Option', 'id display')


class SelectField(Field):
  def __init__(self, *args, **kwargs):
    self.options = kwargs.pop('options', [])
    super().__init__(*args, **kwargs)

  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    if self.value:
      if not self.options:
        return 'This select has no options'
      for option in self.options:
        if self._is_selected_option(option):
          return
      return '{} is not in the list of options'.format(self.value)

  def _is_selected_option(self, option):
    # option.id is probably an int because it probably came from objects, while
    # self.value is probably a string when it comes from the browser but
    # probably an int when it comes from tests and business logic.
    return self._value_set and str(option.id) == str(self.value)

  def _is_default_option(self, option):
    return option.id == self.default

  def widget_html(self):
    render = ['<select name="{}">'.format(self.key())]
    if not self.required:
      render.append('<option>-</option>')
    for option in self.options:
      selected_string = ''
      if self._is_selected_option(option) or (
          (not self._value_set) and self._is_default_option(option)):
        selected_string = ' selected="selected"'
      render.append('<option value="{}"{}>{}</option>'.format(
          option.id, selected_string, option.display))
    render.append('</select>')
    return '\n'.join(render)


def date_to_datefield_string(day):
  return day.strftime('%Y-%m-%d')


def datefield_string_to_date(day_string):
  return parse_date(day_string)


class HtmlInputField(Field):
  """ This is for fields that start with <input type="... """
  def widget_html(self):
    value_string = ''
    value_attr = ''
    if self._value_set:
      if self.value is not None:
        value_string = self.value
    elif self.default:
      value_string = self.default
    if value_string:
      value_attr = ' value="{}"'.format(value_string)
    return '<input type="{}"{} name="{}" class="{}"{}>'.format(
        self.input_type(), self.additional_attrs_str(), self.key_prefix,
        self.key(), value_attr)

  def input_type(self):
    raise NotImplementedError('input_type')

  def additional_attrs_str(self):
    raise NotImplementedError('additional_attrs_str')


class DateField(HtmlInputField):
  def set_value(self, value):
    if not value:
      return super().set_value(value)
    if isinstance(value, str):
      return super().set_value(datefield_string_to_date(value))
    if not isinstance(value, date):
      raise Exception(
          'You should set the value of a DateField to None, empty string, a '
          'date object, or a string in the format yyyy-mm-dd')

  def as_csv(self):
    if self.value is not None:
      return self.value.strftime('%Y-%m-%d')
    return ''

  def input_type(self):
    return 'date'

  def additional_attrs_str(self):
    return ' step="0.25" min="0"'


class PositiveFloatField(HtmlInputField):
  def set_value(self, value):
    if value in [None, ''] or isinstance(value, float):
      return super().set_value(value)
    if isinstance(value, str):
      try:
        return super().set_value(float(value))
      except ValueError:
        raise Exception((
            'I can not parse the string {} as a float in '
            'field {}').format(html.escape(value), self.key()))
    raise Exception(
        'You should set the value of a PositiveFloatField to a float')

  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    try:
      float(self.value)
    except ValueError:
      return 'I can not convert {} to a float'.format(html.escape(self.value))
    if self.value < 0:
      return '{} is less than 0'.format(self.value)

  def input_type(self):
    return 'number'

  def additional_attrs_str(self):
    return ' step="0.25" min="0"'
