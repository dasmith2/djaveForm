from djaveClassMagic.model_fields import (
    ModelField, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN)
from djaveForm.field import (
    DateField, PositiveFloatField, PositiveIntField, TextAreaField, TextField,
    TrueFalseField)


def default_widget(model_field):
  if not isinstance(model_field, ModelField):
    raise Exception((
        'I expect model_field to be a '
        'djaveClassMagic.model_fields.ModelField, '
        'not a {}').format(model_field.__class__))

  required = model_field.required
  if model_field.type == DATE:
    return DateField(model_field.name, required=required)
  elif model_field.type == FLOAT:
    return PositiveFloatField(model_field.name, required=required)
  elif model_field.type == INTEGER:
    return PositiveIntField(model_field.name, required=required)
  elif model_field.type == TEXT:
    return TextAreaField(model_field.name, required=required)
  elif model_field.type == CHAR:
    return TextField(model_field.name, required=required)
  elif model_field.type == BOOLEAN:
    return TrueFalseField(model_field.name)
  else:
    raise Exception('I dont know what widget to use for a {} field'.format(
        model_field.type))
