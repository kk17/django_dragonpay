from django.contrib import admin

from django_dragonpay.models import *


class PayoutUserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'email')


class TransactionAdmin(admin.ModelAdmin):
    search_fields = ('id', 'email')


class PayoutsAdmin(admin.ModelAdmin):
    search_fields = ('txn_id', 'user_id', 'user_name', 'email')


admin.site.register(DragonpayPayoutUser, PayoutUserAdmin)
admin.site.register(DragonpayTransaction, TransactionAdmin)
admin.site.register(DragonpayPayouts, PayoutsAdmin)
