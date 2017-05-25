import logging

from django.views import generic
from django.conf import settings

from django_dragonpay.forms import DragonpayCallbackForm
from django_dragonpay.models import DragonpayTransaction

logger = logging.getLogger('django_dragonpay.views')


class DragonpayCallbackHandler(generic.View):
    '''Base view to handle Dragonpay callback transactions that
    updates the transactions in database.

    Usage:
        Inherit the class based view and implement your
        own GET and POST handlers

        class MyDragonpayCallback(DragonpayCallback):
            allow_invalid_data = False  # raise Error if data is invalid

            def get(self, request, *args, **kwargs):
                # the processed form may be access via
                self.form

                # do your stuff here
                pass

            def post(self, request, *args, **kwargs)
                pass
    '''

    allow_invalid_data = True    # should we crash if the data is invalid?

    def dispatch(self, *args, **kwargs):
        # if save data settings is enabled, update the
        # DragonpayTransaction row for this transaction

        if settings.DRAGONPAY_SAVE_DATA:
            self.form = DragonpayCallbackForm(
                self.request.POST or self.request.GET)

            if not self.form.is_valid():
                logger.error(
                    'Invalid Dragonpay callback request: %s', self.form.error)

                if not self.allow_invalid_data:
                    raise Exception('Invalid Dragonpay request')
            else:
                try:
                    txn = DragonpayTransaction.objects.get(
                        id=self.form.cleaned_data['txnid'])
                except DragonpayTransaction.DoesNotExist as e:
                    if not self.allow_invalid_data:
                        raise e
                else:
                    # update the status of the transaction
                    txn.status = self.form.cleaned_data['status']
                    txn.save(update_fields=['status'])

        return super(DragonpayCallbackHandler, self).dispatch(*args, **kwargs)
