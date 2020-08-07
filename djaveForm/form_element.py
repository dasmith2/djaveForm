from abc import abstractmethod

from djaveTable.cell_content import CellContent


class FormElement(CellContent):
  """ A FormElement is a button or html input that can be rendered in the cell
  of a djaveTable, and when the form submits, the FormElement will be
  represented in the data that goes to the server. """
  def __init__(self, key_prefix, pk, additional_attrs=None):
    self.key_prefix = key_prefix
    self.pk = pk
    self.additional_attrs = additional_attrs

  def key(self):
    """ This is the html key used for stuff like <input name={{ key }}> """
    if self.key_prefix:
      if self.pk:
        return '{}_{}'.format(self.key_prefix, self.pk)
      return self.key_prefix
    return ''

  def additional_attrs_str(self):
    if self.additional_attrs:
      linear = []
      for key, value in self.additional_attrs.items():
        linear.append('{}="{}"'.format(key, value))
      return ' {}'.format(' '.join(linear))
    return ''

  @abstractmethod
  def as_html(self):
    raise NotImplementedError('as_html')

  def __eq__(self, other):
    if self.__class__ != other.__class__:
      raise Exception('I do not know how to compare a {} to a {}'.format(
          self.__class__, other.__class__))
    return self.as_html() == other.as_html()

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()
