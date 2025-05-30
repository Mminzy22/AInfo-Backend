from django.contrib import admin

from .models import CurrentStatus, EducationLevel, Interest, Region, SubRegion, User


@admin.register(CurrentStatus)
class CurrentStatusAdmin(admin.ModelAdmin):
    pass


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    pass


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    pass


@admin.register(SubRegion)
class SubRegionAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass
