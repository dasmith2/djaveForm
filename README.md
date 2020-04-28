Django forms are confusing. One classic example:

    my_form.cleaned_data  # Triggers validation

Here's another one. What is this even doing?

    FooFormset = forms.modelformset_factory(Foo, fields=('label',))

Also, I don't remember the specifics, but I did hit a dead end one time related
to testing. Something about trying to combine a form with a dictionary of data
triggered errors, I don't know.

At this point I'm happiest just starting my own library from scratch.

Code needs to make sense in tests as well as in production. The use cases are
roughly

1. You view the form for the first time. Fields are set to the default. No validation has taken place yet so no red text should appear.
1. You combine a form with POST data. Now you can ask if the form is valid, or ask if specific fields are valid.
1. You combine a form with a dictionary in a test. Now you can verify that the form is correctly valid or not, or if the fields are valid or not.
1. If you render a form that was combined with data, the fields should display red error text explaining the problems, if any.
