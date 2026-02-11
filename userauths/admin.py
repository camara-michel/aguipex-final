from django.contrib import admin
from userauths.models import User, Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user', 'get_occupation', 'date']

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Nom complet'

    def get_occupation(self, obj):
        return obj.user.occupation
    get_occupation.short_description = 'Occupation'

class UserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'occupation', 'departement', 'grade', 'est_employer', 'cellule']

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)