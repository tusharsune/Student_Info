from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    actions = ['deactivate_users']

    def deactivate_users(self, request, queryset):
        """Custom action to deactivate selected users"""
        queryset.update(is_active=False)
        self.message_user(request, "Successfully deactivated users.")

    deactivate_users.short_description = "Deactivate selected users"

admin.site.register(User, CustomUserAdmin)
