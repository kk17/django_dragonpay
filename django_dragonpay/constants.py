# Dragonpay error codes.
# See Appendix 2 of Dragonpay API documentation
DRAGONPAY_ERROR_CODES = {
    '000': 'Success',
    '101': 'Invalid payment gateway id',
    '102': 'Incorrect secret key',
    '103': 'Invalid reference number',
    '104': 'Unauthorized access',
    '105': 'Invalid token',
    '106': 'Currency not supported',
    '107': 'Transaction cancelled',
    '108': 'Insufficient funds',
    '109': 'Transaction limit exceeded',
    '110': 'Error in operation',
    '111': 'Invalid parameters',
    '201': 'Invalid Merchant Id',
    '202': 'Invalid Merchant Password'
}

# Dragonpay status codes
# See Appendix 3 of Dragonpay API documentation
DRAGONPAY_STATUS_CODES = {
    'S': 'Success',
    'F': 'Failure',
    'P': 'Pending',
    'U': 'Unknown',
    'R': 'Refund',
    'K': 'Chargeback',
    'V': 'Void',
    'A': 'Authorized'
}

# Dragonpay Paymemnt method FILTERS
ONLINE_BANKING = 1       # Online banking
OTC_BANK = 2             # Over-the-Counter Banking and ATM
OTC_NON_BANK = 4         # Over-the-Counter non-Bank
# 8 (unused)
# 16 (reserved internally)
PAYPAL = 32              # PayPal
CREDIT_CARDS = 64        # Credit Cards
MOBILE = 128             # Mobile (Gcash)
INTERNATIONAL_OTC = 256  # International OTC
