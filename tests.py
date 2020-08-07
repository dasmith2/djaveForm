import unittest

from djaveForm.button import Button
from djaveForm.field import PositiveFloatField
from djaveForm.form import Form


class Tests(unittest.TestCase):
  def test_blank_required_field_invalid_form(self):
    pos_float_field = PositiveFloatField(
        key_prefix='hours', required=True, default=0.0)
    save_button = Button('Save')
    self.assertEqual('save', save_button.key())
    self.assertEqual('hours', pos_float_field.key())

    form = Form([pos_float_field, save_button])
    try:
      form.is_valid()
      self.fail(
          'I have not set the form data so I should not be able to ask if '
          'the form is valid')
    except Exception:
      pass
    form.set_form_data({'hours': '', 'save': 'save'})
    self.assertFalse(form.is_valid())
    self.assertFalse(pos_float_field.is_valid())
    if not 'problem' in pos_float_field.as_html():
      self.fail(
          'The positive float field does not appear to display the '
          'validation problem')


if __name__ == '__main__':
  unittest.main()
