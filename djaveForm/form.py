from djaveForm.button import Button
from djaveForm.field import Field


class Form(object):
  def __init__(self, form_elements):
    self.form_elements = form_elements

  def is_valid(self):
    valid_so_far = True
    for form_element in self.form_elements:
      if isinstance(form_element, Field):
        valid_so_far = valid_so_far and form_element.is_valid()
    return valid_so_far

  def set_form_data(self, values):
    for form_element in self.form_elements:
      if form_element.key() in values:
        if isinstance(form_element, Button):
          form_element.set_was_clicked(form_element.key() in values)
        elif isinstance(form_element, Field):
          form_element.set_value(values[form_element.key()])
        else:
          raise Exception('I do not know how to set the value of a {}'.format(
              form_element.__class__))
