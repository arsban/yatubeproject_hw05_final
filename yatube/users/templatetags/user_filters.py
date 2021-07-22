from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def uglify(uglify):
    count = 0
    letters_string = ''

    for letters in uglify:
        count += 1
        if count % 2 == 0:
            letters_string += letters.upper()

        else:
            letters_string += letters.lower()
    return letters_string
