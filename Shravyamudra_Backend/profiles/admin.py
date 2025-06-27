from django.contrib import admin
from .models import Profile

import csv
from django.http import HttpResponse

from django.contrib.admin import SimpleListFilter

class AvatarPresenceFilter(SimpleListFilter):
    title = 'Has Avatar'
    parameter_name = 'has_avatar'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'yes':
            return queryset.exclude(avatar='')
        if value == 'no':
            return queryset.filter(avatar='')
        return queryset

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'accountType', 'memberSince', 'avatarUrl', 'bio', 'has_avatar')
    search_fields = ('user__username', 'accountType', 'user__email')
    list_filter = ('accountType', AvatarPresenceFilter)

    actions = ['export_profiles_csv', 'download_profile_emails']

    def has_avatar(self, obj):
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Has Avatar'

    def export_profiles_csv(self, request, queryset):
        field_names = ['user', 'accountType', 'memberSince', 'avatarUrl', 'bio']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=profiles.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([
                obj.user.username,
                obj.accountType,
                obj.memberSince,
                obj.avatarUrl,
                obj.bio,
            ])
        return response
    export_profiles_csv.short_description = "Export Selected Profiles as CSV"

    def download_profile_emails(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=profile_emails.csv'
        writer = csv.writer(response)
        writer.writerow(['username', 'email'])
        for obj in queryset:
            writer.writerow([obj.user.username, obj.user.email])
        return response
    download_profile_emails.short_description = "Download Emails of Selected Profiles as CSV"

admin.site.register(Profile, ProfileAdmin)

