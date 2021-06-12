from django.contrib import admin
from .models import User, Movie, ContactInfo, Address

admin.site.register(User)
admin.site.register(ContactInfo)
admin.site.register(Address)
admin.site.register(Movie)

