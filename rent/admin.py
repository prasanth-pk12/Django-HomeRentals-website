from django.contrib import admin
from .models import room,District,State,Locations,Temporary,City,Gallerys
from django.contrib.admin.options import ModelAdmin



class roomAdmin(ModelAdmin):
    list_display = ['id','Owner_Name','city','House_address','phone_no']
    search_fields = ['Owner_Name','city','House_address','phone_no']
admin.site.register(room,roomAdmin)


class TemporaryAdmin(ModelAdmin):
    list_display = ['id','Owner_Name','state','district','city','House_address','phone_no']
    search_fields = ['Owner_Name','city','House_address','phone_no']
admin.site.register(Temporary,TemporaryAdmin)


class StateAdmin(ModelAdmin):
    list_display = ['id','name']
    search_fields = ['name']
admin.site.register(State,StateAdmin)

class DistrictAdmin(ModelAdmin):
    list_display = ['id','name','state']
    search_fields = ['name','state']
admin.site.register(District,DistrictAdmin)


class LocationsAdmin(ModelAdmin):
    list_display = ['id','name','city']
    search_fields = ['name','city']
admin.site.register(Locations,LocationsAdmin)



class CityAdmin(ModelAdmin):
    list_display = ['id','name','dist']
    search_fields = ['name','dist']
admin.site.register(City,CityAdmin)


admin.site.register(Gallerys)
