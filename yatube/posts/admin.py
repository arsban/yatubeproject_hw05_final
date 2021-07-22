from django.contrib import admin

from .models import Group, Post

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "related_group")
    search_fields = ("text",)
    list_filter = ("pub_date", "group",)
    empty_value_display = "-пусто-"

    def related_group(self, obj):
        if obj.group is not None:
            return "(id:{}) {}".format(obj.group.id, obj.group.title)
        else:
            return self.popup_response_template
    related_group.short_description = "group"

    def get_form(self, request, obj=None, **kwargs):
        form = super(PostAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['group'].label_from_instance = (
            lambda obj: "{} {}".format(obj.id, obj.title))
        return form


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
