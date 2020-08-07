from djaveForm.button import Button
from djaveForm.field import Field, TrueFalseField
from djaveURL import dict_as_query


class Form(object):
  """ Forms don't know about display. You don't call my_form.as_html. Where
  Django forms get it wrong is their assumption that there's a simple rendering
  function or two that are good enough for all forms. In my experience, your
  website will be much better if you put thought into how each form will be
  uniquely laid out. """
  def __init__(self, form_elements=None):
    form_elements = form_elements or []
    self.form_elements = form_elements
    self._form_data_set = False

  def new_form_element(self, new_form_element):
    self.form_elements.append(new_form_element)
    return new_form_element

  def is_valid(self):
    valid_so_far = True
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        valid_so_far = valid_so_far and form_element.is_valid()
    return valid_so_far

  def explain_why_not_valid(self):
    to_return = []
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        explanation = form_element.explain_why_not_valid()
        if explanation:
          to_return.append(explanation)
    return ', '.join(to_return) or None

  def a_button_was_clicked(self, post_data):
    """ If you've got multiple forms on a page, you might want to check which
    form has a button that appears in the post data so you don't end up
    validating a form that wasn't actually clicked. """
    if not post_data:
      return False
    for element in self.form_elements:
      if isinstance(element, Button):
        if element.get_was_clicked(post_data):
          return True
    return False

  def form_data_was_set(self):
    return self._form_data_set

  def set_form_data(self, values):
    values = values or {}
    self._form_data_set = True
    for form_element in self.form_elements:
      key_present = form_element.key() in values
      if isinstance(form_element, Button):
        form_element.set_was_clicked(key_present)
      elif isinstance(form_element, TrueFalseField):
        form_element.set_value(key_present)
      elif key_present:
        if isinstance(form_element, Field):
          form_element.set_value(values[form_element.key()])
        else:
          raise Exception('I do not know how to set the value of a {}'.format(
              form_element.__class__))

  def to_query_string(self):
    return dict_as_query(self.to_dict())

  def to_dict(self):
    _dict = {}
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        _dict[form_element.key()] = form_element.get_value_or_default()
    return _dict
