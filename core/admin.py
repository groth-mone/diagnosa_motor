#core/admin.py
from django.contrib import admin
from .models import Gejala, Diagnosa, Rule

admin.site.register(Gejala)
admin.site.register(Diagnosa)
admin.site.register(Rule)