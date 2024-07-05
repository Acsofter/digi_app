from django.contrib import admin
from .models import User, Company, Ticket

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Company)

