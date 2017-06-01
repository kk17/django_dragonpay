Creating a DragonPay Callback Handler
-

### Overview

Every after succsesful transaction update (Success, Pending, Canceled), DragonPay sends a HTTP POST request to your application's registered callback handler about the transaction update. This data can be processed by the `DragonpayCallbackForm` form. Subsequently, most times DragonPay also redirects the user to your registered callback handler containing the same data in the POST request.

The HTTP POST request will almost always be before the GET redirect, unless on cases where latency/traffic volume is high.

Because of this, it is suggested that all transaction updates to the database be done during POST requests, and only show informational messages or content when a GET redirect is receieved.

### Creating a Handler

To help you handle requests on your Dragonpay Callback URL, you should create your own CallbackHandler inheriting the `DragonpayCallbackBaseHandler` class. `DragonpayCallbackBaseHandler` does a preprocessing on the request using the `DragonpayCallbackForm` as well as updates the `DragonpayTransaction` or `DragonpayPayout` tables. This is useful when you use the `DragonpayTransaction` table as your main transaction storage facility. Here is a sample CallbackHandler:

    from django_dragonpay.views import DragonpayCallbackBaseHandler

    class MyDragonpayCallbackHander(DragonpayCallbackBaseHandler):
        def get(self, request, *args, **kwargs):
            form = self.form        # form processed by BaseHandler

            if form.cleaned_data['status'] == 'S'
                return HttpResponse('Transaction successful')

            elif form.cleaned_data['status'] == 'P':
                return HttpResponse('Please check your email to complete the transaction)'
            elif form.cleaned_data['status'] != 'S':
                if 'canceled' in form.cleaned_data['message']:
                    return HttpResponse('You have canceled the transaction')

        def post(self, request, *args, **kwargs):
            form = self.form

            # if you need to modify your transaction tables
            # do it here. You may use the same if statements
            # from the get method above.

            return HttpResponse('OK')


#### Pre-processing during dispatch

`DragonpayCallbackBaseHandler` is an instance of `django.view.generic.View` and does the pre-processing in the dispatch method. If you plan to override the dispatch method, don't forget to call the parent class' dispatch method

    class MyDragonpayCallbackHander(DragonpayCallbackBaseHandler):
        # Overriding the dispatch method
        def dispatch(self, *args, **kwargs):
            # call the parent's dispatch before doing anything else
            super(MyDragonpayCallbackHander, self).dispatch(*args, **kwargs)

##### update\_on\_GET

**DragonpayCallbackBaseHandler** will update the *Transaction* and *Payout* tables if the **DRAGONPAY\_SAVE\_DATA** settings is set to *True*. The tables will only be updated when an instance of `DragonpayCallbackBaseHandler` is called during the POST request. To enable updating the database during GET request, set the **update\_on\_GET** parameter to *True*.

        class MyDragonpayCallbackHander(DragonpayCallbackBaseHandler):
            update_on_GET = True

            ...

##### allow\_invalid\_data

By default, **DragonpayCallbackBaseHandler** will allow invalid data to be sent without raising an exception. In this case, it is assumed that your CallbackHandler should be able to handle invalid forms. If you wish to raise an exception if the request data (GET or POST) sent to the handler is not valid, set the **allow\_invalid\_data** to *False*.

        class MyDragonpayCallbackHander(DragonpayCallbackBaseHandler):
            allow_invalid_data = False

            ...




