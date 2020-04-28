from djaveTable.cell_content import CellContent


class FormElement(CellContent):
  """ A FormElement is a button or html input that can be rendered in the cell
  of a djaveTable, and when the form submits, the FormElement will be
  represented in the data that goes to the server. """
  def __init__(self, key_prefix, pk):
    self.key_prefix = key_prefix
    self.pk = pk

  def key(self):
    if self.key_prefix:
      if self.pk:
        return '{}_{}'.format(self.key_prefix, self.pk)
      return self.key_prefix
    return ''
