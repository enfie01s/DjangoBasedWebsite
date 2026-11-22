from django.contrib import admin
from .models import SitePlayer,Rank,World,SitePerm,GPplayer


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player','rank')
class SitePermAdmin(admin.ModelAdmin):
    list_display = ('perm','comm','descrip','minrank')
class GPplayerAdmin(admin.ModelAdmin):
    list_display = ('name','uuid','lastlogin','accruedblocks','bonusblocks')

# Register your models here.
admin.site.register(SitePlayer,PlayerAdmin)
admin.site.register(Rank)
admin.site.register(World)
admin.site.register(SitePerm,SitePermAdmin)
admin.site.register(GPplayer,GPplayerAdmin)