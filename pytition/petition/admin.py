from django.contrib import admin

from petition.models import Signature, Petition


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display =  ('first_name', 'last_name', 'phone', 'email', 'confirmed', 'subscribed_to_mailinglist', 'petition')


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    pass