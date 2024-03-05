from django.contrib import admin
from .models import Pgs_Data,Room_Info,Guest_Info,AppUser
# Register your models here.
admin.site.register(Pgs_Data)
admin.site.register(Room_Info)
admin.site.register(Guest_Info)
admin.site.register(AppUser)

