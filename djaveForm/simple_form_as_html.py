from djaveTable.simple_list import SimpleList


def simple_form_as_html(form):
  return SimpleList(form.form_elements).as_html()
