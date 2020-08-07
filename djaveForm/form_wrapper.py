""" This basically does
<form method="POST">
  {% csrf_token %}
  {{ wrap_around.as_html }}
</form> """
from django.template.loader import render_to_string


class FormWrapper(object):
  def __init__(self, wrap_around, request):
    self.wrap_around = wrap_around
    self.request = request

  def as_html(self):
    return render_to_string(
        'form_wrapper.html', {'wrap_around': self.wrap_around},
        request=self.request)
