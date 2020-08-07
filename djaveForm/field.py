from collections import namedtuple
from datetime import date
import html
import re

from django.utils.dateparse import parse_date
from django.utils.safestring import mark_safe
from djaveForm.form_element import FormElement
from djaveTable.problem import Problem


class Field(FormElement):
  # You can put djaveForm fields in djaveTables.
  def __init__(
      self, key_prefix, required=True, default=None, pk=None, value=None,
      label=None, autofocus=False):
    super().__init__(key_prefix, pk)
    self.required = required
    self.default = default

    self._value = None
    self._value_set = False
    if value is not None and value != '':
      self.set_value(value)

    self.label = label
    self.autofocus = autofocus

    self._custom_invalid_reason = None

  def set_value(self, value):
    if value == '':
      self._value = None
    else:
      self._value = value
    self._value_set = True

  def get_value(self):
    if not self._value_set:
      raise Exception(
          'You have to set the value of a field before you can get the value '
          'of a field. You probably want to call set_form_data on the form.')
    return self._value

  def value_was_set(self):
    return self._value is not None

  def get_value_string(self):
    if self._value_set:
      if self.get_value() is not None:
        return self.get_value()
    elif self.default:
      return self.default
    return ''

  def get_value_or_default(self):
    if self._value_set:
      return self.get_value()
    return self.default

  def explain_why_not_valid(self):
    if self.required and not self.get_value():
      return 'Required'
    if self._custom_invalid_reason:
      return self._custom_invalid_reason

  def set_invalid_reason(self, reason):
    self._custom_invalid_reason = reason

  def is_valid(self):
    if not self._value_set:
      raise Exception((
          'The value of field with key {} was never set, so it does not make '
          'much sense to ask if the field is valid.').format(self.key()))
    return not self.explain_why_not_valid()

  def as_csv(self):
    if self.get_value() is None:
      return ''
    return str(self.get_value())

  def as_html(self):
    widget_html = self.widget_html()
    error_html = ''
    if self._value_set:
      why_invalid = self.explain_why_not_valid()
      if why_invalid:
        error_html = Problem(why_invalid).as_html()
    html = '{}\n{}'.format(widget_html, error_html)
    if self.label:
      html = '<label>{} {}</label>'.format(self.label, html)
    return mark_safe(html)

  def widget_html(self):
    raise NotImplementedError('widget_html')

  def autofocus_str(self):
    if self.autofocus:
      return ' autofocus'
    return ''


Option = namedtuple('Option', 'id display')


class SelectField(Field):
  def __init__(self, *args, **kwargs):
    self.options = kwargs.pop('options', [])
    super().__init__(*args, **kwargs)

  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    if self.get_value():
      if not self.options:
        return 'This select has no options'
      for option in self.options:
        if self._is_selected_option(option):
          return
      return '{} is not in the list of options'.format(self.get_value())

  def _is_selected_option(self, option):
    # option.id is probably an int because it probably came from objects, while
    # self.get_value() is probably a string when it comes from the browser but
    # probably an int when it comes from tests and business logic.
    return self._value_set and str(option.id) == str(self.get_value())

  def _is_default_option(self, option):
    """ SelectField is useful for picking an object. So it totally makes sense
    to use an object as the default. """
    if hasattr(self.default, 'id'):
      return option.id == self.default.id
    return option.id == self.default

  def widget_html(self):
    render = ['<select name="{}"{}>'.format(self.key(), self.autofocus_str())]
    if not self.required:
      render.append('<option></option>')
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


class TextAreaField(Field):
  def widget_html(self):
    return '<textarea name="{}" class="{}"{}>{}</textarea>'.format(
        self.key(), self.key_prefix, self.autofocus_str(),
        self.get_value_string())


class HtmlInputField(Field):
  """ This is for fields that start with <input type="... """
  def widget_html(self):
    return '<input type="{}"{} name="{}" class="{}"{}{}>'.format(
        self.input_type(), self.additional_attrs_str(), self.key(),
        self.key_prefix, self.get_value_html_str(), self.autofocus_str())

  def get_value_html_str(self):
    return ' value="{}"'.format(self.get_value_string())

  def input_type(self):
    raise NotImplementedError('input_type')

  def additional_attrs_str(self):
    return ''


class TrueFalseField(HtmlInputField):
  """ As opposed to a True/False/Unspecified field. """
  def __init__(self, *args, **kwargs):
    if 'required' not in kwargs:
      kwargs['required'] = False
    if 'default' in kwargs:
      raise Exception(
          'TrueFalseFields cant have a default because, in form post data, '
          'theres no way to distinguish between unset and False')
    kwargs['default'] = False
    super().__init__(*args, **kwargs)

  def is_valid(self):
    """  This field is a little wacky in that, when the form returns nothing
    whatsoever, that's assumed to be false. So within this field I can't tell
    if you never passed in the form or it's just false. """
    return True

  def get_value_html_str(self):
    if self.get_value_or_default():
      return ' checked'
    return ''

  def set_value(self, value):
    super().set_value(bool(value))

  def input_type(self):
    return 'checkbox'


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
    if self.get_value() is not None:
      return self.get_value().strftime('%Y-%m-%d')
    return ''

  def input_type(self):
    return 'date'


class TextField(HtmlInputField):
  def input_type(self):
    return 'text'


class HiddenField(HtmlInputField):
  def input_type(self):
    return 'hidden'


class SlugField(TextField):
  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    if re.compile(r'[^\w-]').findall(self.get_value()):
      return 'You can only use letters, numbers, _ and -'


class URLField(TextField):
  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    if self.get_value():
      if self.get_value().find('http') != 0:
        return 'This should be a URL, like, https://whatever'


class NumberField(HtmlInputField):
  def set_value(self, value):
    if value in [None, ''] or isinstance(value, self.cast_function()):
      return super().set_value(value)
    if isinstance(value, str):
      try:
        return super().set_value(self.cast_value(value))
      except ValueError:
        raise Exception('I can not parse {} as a {} in field {}'.format(
            html.escape(value), self.cast_function().__name__, self.key()))
    raise Exception(
        'You should set the value of a {} to a {}'.format(
            self.__class__.name, self.cast_function().__name__))

  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    try:
      self.cast_value(self.get_value())
    except ValueError:
      return 'I can not convert {} to a {}'.format(
          html.escape(self.get_value()), self.cast_function().__name__)

  def input_type(self):
    return 'number'

  def additional_attrs_str(self):
    return ' step="{}"'.format(self.get_step())

  def cast_value(self, value):
    return self.cast_function()(value)

  def cast_function(self):
    raise NotImplementedError('cast_function')

  def get_step(self):
    raise NotImplementedError('get_step')


class FloatField(NumberField):
  def cast_function(self):
    return float

  def get_step(self):
    return 0.01


class MoneyField(FloatField):
  def widget_html(self):
    return '${}'.format(super().widget_html())


class IntField(NumberField):
  def cast_function(self):
    return int

  def get_step(self):
    return 1


class PositiveNumberField(NumberField):
  def explain_why_not_valid(self):
    super_invalid = super().explain_why_not_valid()
    if super_invalid:
      return super_invalid
    if self.get_value() < 0:
      return '{} is less than 0'.format(self.get_value())

  def additional_attrs_str(self):
    return ' step="{}" min="0"'.format(self.get_step())


class PositiveFloatField(PositiveNumberField):
  def cast_function(self):
    return float

  def get_step(self):
    return 0.01


class PositiveIntField(PositiveNumberField):
  def cast_function(self):
    return int

  def get_step(self):
    return 1
