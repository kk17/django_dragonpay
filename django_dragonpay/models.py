from django.db import models
from django.conf import settings

from django_dragonpay.api.soap import get_txn_status

__all__ = ['DragonpayPayoutUser', 'DragonpayTransaction', 'DragonpayPayout']


class DragonpayPayoutUser(models.Model):
    first_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    email = models.CharField(max_length=64)
    birthdate = models.DateField()
    mobile = models.CharField(max_length=24)
    address1 = models.CharField(max_length=32)
    address2 = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=16)
    state = models.CharField(max_length=16)
    zip = models.CharField(max_length=8)


class DragonpayTransaction(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='PHP')
    description = models.CharField(max_length=128)
    email = models.CharField(max_length=40)
    param1 = models.CharField(max_length=80, null=False, blank=True)
    param2 = models.CharField(max_length=80, null=False, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField()

    def __unicode__(self):
        return '[%s:%s] %s' % (self.id, self.amount, self.description)

    def get_status(self):
        return get_txn_status(self.id)

    @classmethod
    def create_from_dict(cls, details):
        # Check if we should save to database
        if not settings.DRAGONPAY_SAVE_DATA:
            return

        return DragonpayTransaction.objects.create(
            id=details['txn_id'],
            amount=details['amount'],
            currency=details.get('currency'),
            description=details['description'],
            email=details['email'],
            param1=details.get('param1'),
            param2=details.get('param2'),
        )


class DragonpayPayout(models.Model):
    txn_id = models.CharField(max_length=40)

    # For payout registerd user
    user_id = models.CharField(max_length=40, null=True, blank=True)

    # For non-registered, one time payout
    user_name = models.CharField(max_length=32, null=True, blank=True)
    processor_id = models.CharField(max_length=8, null=True, blank=True)
    processor_detail = models.CharField(max_length=32, null=True, blank=True)
    email = models.CharField(max_length=32, null=True, blank=True)
    mobile = models.CharField(max_length=32, null=True, blank=True)

    # payout details
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=128)
    currency = models.CharField(max_length=3, default='PHP')

    created_at = models.DateTimeField(auto_now_add=True)    # timestamp field
    completed_at = models.DateTimeField()

    @classmethod
    def create_from_dict(cls, details):
        # Check if we should save to database
        if not settings.DRAGONPAY_SAVE_DATA:
            return

        payouts = []
        if isinstance(details, dict):
            # request is for a single payout
            # it may be registered, or non-registered payout user
            return DragonpayPayout.objects.create(
                txn_id=details['txn_id'],
                user_id=details.get('user_id'),
                user_name=details.get('user_name'),
                processor_id=details.get('processor_id'),
                processor_detail=details.get('processor_detail'),
                timestamp=details.get('timestamp'),
                email=details.get('email'),
                mobile=details.get('mobile'),
                amount=details['amount'],
                description=details['description'],
                currency=details.get('currency'),
                created_at=details['timestamp'],
            )

        elif isinstance(details, list):
            # request is from MultiplePayout; iterate over the details
            for detail in details:
                payouts.append(
                    DragonpayPayout.objects.create(
                        txn_id=detail['txn_id'],
                        user_id=detail['user_id'],
                        amount=detail['amount'],
                        description=detail['description'],
                        currency=detail.get('currency'),
                        created_at=detail['timestamp'],
                    ))

            return payouts

        else:
            raise Exception('Invalid details type %s', type(details))
