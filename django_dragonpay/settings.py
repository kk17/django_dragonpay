from django.conf import settings

# DRAGONPAY API
DRAGONPAY_TEST_MODE = getattr(settings, 'DRAGONPAY_TEST_MODE', False)
DRAGONPAY_MERCHANT_ID = getattr(settings, 'DRAGONPAY_MERCHANT_ID')
DRAGONPAY_MERCHANT_PASSWORD = getattr(settings, 'DRAGONPAY_MERCHANT_PASSWORD')
DRAGONPAY_API_KEY = getattr(settings, 'DRAGONPAY_API_KEY')
DRAGONPAY_ENCRYPT_PARAMSS = getattr(settings, 'DRAGONPAY_ENCRYPT_PARAMSS', False)

if DRAGONPAY_TEST_MODE:
    DRAGONPAY_BASE_URL = 'http://test.dragonpay.ph/'
else:
    DRAGONPAY_BASE_URL = 'https://gw.dragonpay.ph/'

# Other Dragonpay URLs
DRAGONPAY_PAY_URL = DRAGONPAY_BASE_URL + 'Pay.aspx'
DRAGONPAY_MERCHANT_URL = DRAGONPAY_BASE_URL + 'MerchantRequest.aspx'
DRAGONPAY_SOAP_URL = DRAGONPAY_BASE_URL + 'DragonPayWebService/MerchantService.asmx'
DRAGONPAY_PAYOUT_URL = DRAGONPAY_BASE_URL + 'DragonPayWebService/PayoutService.asmx'
