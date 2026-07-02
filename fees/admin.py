from django.contrib import admin
from .models import FeeCategory, FeePayment

admin.site.register(FeeCategory)
admin.site.register(FeePayment)
