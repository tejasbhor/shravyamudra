from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from profiles.models import Profile

User = get_user_model()

# Customize admin site
admin.site.site_header = 'Shravya Mudra Admin'
admin.site.site_title = 'Shravya Mudra Admin Portal'
admin.site.index_title = 'Welcome to Shravya Mudra Admin Portal'

# Custom admin branding: logo and CSS
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html

class CustomAdminSite(admin.AdminSite):
    site_header = 'Shravya Mudra Admin'
    site_title = 'Shravya Mudra Admin Portal'
    index_title = 'Welcome to Shravya Mudra Admin Portal'

    def each_context(self, request):
        context = super().each_context(request)
        context['site_logo'] = staticfiles_storage.url('admin/logo.png')
        return context

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        return urls

# Use custom admin site if needed (optional, for advanced branding)
# admin.site = CustomAdminSite()

# Inject custom CSS (works for Django >= 2.0)
def custom_admin_css():
    from django.contrib.admin.sites import site
    site.get_urls = lambda: site.get_urls()  # monkeypatch to re-register
    from django.contrib.staticfiles.storage import staticfiles_storage
    return format_html('<link rel="stylesheet" type="text/css" href="{}">', staticfiles_storage.url('admin/custom_admin.css'))

admin.site.register_view = getattr(admin.site, 'register_view', lambda *a, **kw: None)
admin.site.register_view('custom_admin_css', view=None)
admin.site.site_header = 'Shravya Mudra Admin'
admin.site.site_title = 'Shravya Mudra Admin Portal'
admin.site.index_title = 'Welcome to Shravya Mudra Admin Portal'
admin.site.login_template = 'admin/login.html'

# Inject dashboard widget JS into the admin index page
from django.contrib.admin.sites import site as default_site
from django.template.response import TemplateResponse
from django.utils.deprecation import MiddlewareMixin

class DashboardWidgetMiddleware(MiddlewareMixin):
    def process_template_response(self, request, response):
        if request.path == '/admin/' and hasattr(response, 'context_data'):
            extra_js = '<script src="/static/admin/dashboard_widget.js"></script>'
            if 'media' in response.context_data:
                response.context_data['media'] += extra_js
            else:
                response.context_data['media'] = extra_js
        return response

# Optionally, register middleware in settings.py if not using template override

@admin.action(description="Promote selected users to admin")
def promote_to_admin(modeladmin, request, queryset):
    queryset.update(role='admin', is_superuser=True, is_staff=True)

@admin.action(description="Demote selected users to normal user")
def demote_to_user(modeladmin, request, queryset):
    queryset.update(role='user', is_superuser=False, is_staff=False)

@admin.action(description="Activate selected users")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('accountType', 'memberSince', 'avatar_image', 'bio')
    readonly_fields = ('avatar_image',)
    extra = 0

    def avatar_image(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:48px;width:48px;border-radius:50%;object-fit:cover;"/>', obj.avatar.url)
        return ""
    avatar_image.short_description = 'Avatar'
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mass_mail

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'account_type', 'profile_avatar', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'last_login', 'profile_link')
    list_filter = ('role', 'is_superuser', 'is_staff', 'is_active', 'profile__accountType')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__accountType')
    ordering = ('-date_joined',)
    actions = [promote_to_admin, demote_to_user, activate_users, deactivate_users, 'export_as_csv', 'send_notification_email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    inlines = [ProfileInline]
    readonly_fields = ('profile_avatar', 'account_type')

    def profile_avatar(self, obj):
        try:
            if obj.profile.avatar:
                return format_html('<img src="{}" style="height:36px;width:36px;border-radius:50%;object-fit:cover;"/>', obj.profile.avatar.url)
        except Exception:
            pass
        return ""
    profile_avatar.short_description = 'Avatar'

    def account_type(self, obj):
        try:
            return obj.profile.accountType
        except Exception:
            return ""
    account_type.short_description = 'Account Type'

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=users.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = "Export Selected Users as CSV"

    def send_notification_email(self, request, queryset):
        subject = "ShravyaMudra Notification"
        message = "This is a notification from the admin."
        from_email = None
        recipient_list = [u.email for u in queryset if u.email]
        datatuple = [(subject, message, from_email, [email]) for email in recipient_list]
        send_mass_mail(datatuple, fail_silently=True)
        self.message_user(request, f"Sent notification email to {len(recipient_list)} users.", messages.SUCCESS)
    send_notification_email.short_description = "Send notification email to selected users"

    def profile_link(self, obj):
        try:
            return format_html('<a href="/admin/profiles/profile/{}/change/">View/Edit Profile</a>', obj.profile.id)
        except Exception:
            return "No profile"
    profile_link.short_description = 'Profile'

class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20

# Unregister default models
admin.site.unregister(Group)

# Register custom User and Group admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
