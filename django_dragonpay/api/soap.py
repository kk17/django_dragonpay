import json
import string
import random
import urllib
import logging
import requests
from datetime import datetime
import xml.dom.minidom as xmlminidom
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from django.template.loader import render_to_string

from django_dragonpay import settings
from django_dragonpay.utils import encrypt_data
from django_dragonpay.constants import DRAGONPAY_ERROR_CODES

logger = logging.getLogger('dragonpay')

HEADERS = {'Content-Type': 'text/xml'}
CONTEXT = {
    'dp_merchant_id': settings.DRAGONPAY_MERCHANT_ID,
    'dp_merchant_secret': settings.DRAGONPAY_MERCHANT_PASSWORD,
    'dp_merchant_apikey': settings.DRAGONPAY_API_KEY
}


def _dragonpay_soap_wrapper(webmethod, context, xml_name=None, payout=False, **callback):
    '''Wrapper function for SOAP requests to DragonPay Payment Switch (PS)

    webmethod - the DragonPay web method being called.'''

    # include the configuration constants
    context.update(CONTEXT)
    context['web_method'] = webmethod

    xml = render_to_string(
        'dragonpay_soapxml/%s.xml' % xml_name or webmethod, context)

    headers = {'SOAPAction': "http://api.dragonpay.ph/%s" % webmethod}
    headers.update(HEADERS)

    if not payout:
        print "SOAP URL"
        url = settings.DRAGONPAY_SOAP_URL
    else:
        print "Xxxxx--x-x-x"
        url = settings.DRAGONPAY_PAYOUT_URL

    logger.debug(
        'SENDING XML REQUEST [%s]:\n%s', settings.DRAGONPAY_SOAP_URL, xml)

    response = requests.post(url, data=xml, headers=headers)

    try:
        resp_xml = xmlminidom.parseString(response.content)
        resp_xml = resp_xml.toprettyxml()
    except:
        resp_xml = response.content

    if response.status_code != 200:
        logger.error(
            'Invalid response %s:\n%s', response.status_code, resp_xml)

    else:
        logger.debug('Success\n%s', resp_xml)
        xmltree = etree.fromstring(response.content)

        # Call the callback if it exists, else, just return the XMLtree
        if 'success' in callback:
            return callback['success'](xmltree)
        else:
            return xmltree


def _dragonpay_get_wrapper(webmethod, context, payout, **callback):
    '''Dragonpay SOAP wrapper function that returns the result of
    GET WebMethods.'''

    xml_name = 'webmethod'

    if webmethod in ['CancelTransaction', 'RegisterPayoutUser']:
        # Some DragonPay engineer decided that the CancelTransaction
        # should have a different SOAP format than the others
        xml_name = webmethod

    print "PAYOUT", payout
    xmltree = _dragonpay_soap_wrapper(webmethod, context, xml_name, payout, **callback)

    # Parse the response XML for the WebMethod specific response
    if xmltree is not None:
        response = xmltree.find(
            './/{http://api.dragonpay.ph/}%(webmethod)sResponse/'
            '{http://api.dragonpay.ph/}%(webmethod)sResult' % {
                'webmethod': webmethod}
        ).text

        return response


def get_txn_url_from_token(token):
    '''Returns the DragonPay payment URL given a token.'''

    path = urllib.urlencode({'tokenid': token})
    return settings.DRAGONPAY_PAY_URL + '?' + path


def get_txn_token_url(amount, description, email, *params):
    '''Creates a DragonPay transaction and returns the Payment Switch URL.'''

    token = get_txn_token(amount, description, email, *params)[1]

    if token:
        return get_txn_url_from_token(token)


def get_txn_token(amount, description, email, *params):
    '''Requests for a new DragonPay transaction and returns its token.'''

    logger.debug(
        'get_txn_token %s %s %s %s', email, amount, description, params)

    txn_id = ''.join([random.choice(string.hexdigits) for i in range(8)])
    context = {
        'amount': amount, 'email': email,
        'description': 'description', 'txn_id': txn_id
    }

    # include the params in the context
    for i, param in enumerate(params):
        if settings.DRAGONPAY_ENCRYPT_PARAMS:
            # Encrypt the params to obfuscate the payload
            logger.debug('Encrypting %s', param)
            param = encrypt_data(param)

        context['param%s' % (i + 1)] = param

    logger.debug('get_txn_token payload: %s', context)

    token = _dragonpay_get_wrapper('GetTxnToken', context)

    # check if the response token is an error code
    if len(token) < 4:
        logger.error(
            '[%s] Dragonpay Error: %s',
            token, DRAGONPAY_ERROR_CODES[token])

        return

    logger.debug('[%s] token %s for %s PhP %s', txn_id, token, email, amount)

    return txn_id, token


def get_txn_status(txn_id):
    logger.debug('get_txn_status')

    context = {'txn_id': txn_id}
    txn_status = _dragonpay_get_wrapper('GetTxnStatus', context)

    logger.debug('[%s] Txn Status for %s', txn_status, txn_id)
    return txn_status


def cancel_transaction(txn_id):
    logger.debug('cancel_transaction')

    context = {'txn_id': txn_id}
    status = _dragonpay_get_wrapper('CancelTransaction', context)

    if status == '0':
        logger.debug('[%s] Txn cancellation success', txn_id)
        return True

    else:
        logger.debug('[%s] Txn cancellation failed: %s', txn_id, status)


def get_txn_ref_no(txn_id):
    logger.debug('get_txn_ref_no')
    context = {'txn_id': txn_id}

    refno = _dragonpay_get_wrapper('GetTxnRefNo', context)
    logger.debug('[%s] reference no: %s', txn_id, refno)
    return refno


def get_available_processors(amount):
    context = {'amount': amount, 'web_method': 'GetAvailableProcessors'}
    context.update(CONTEXT)

    xml = render_to_string('dragonpay_soapxml/webmethod.xml', context=context)

    def _success(response):
        pass

    def _error(response):
        pass

    return _dragonpay_soap_wrapper(xml, success=_success, error=_error)


def get_email_instructions(refno):
    response = requests.get(
        settings.DRAGONPAY_BASE_URL + 'Bank/GetEmailInstruction.aspx',
        params={'refno': refno, 'format': 'json'})

    if response.status_code == 200:
        return json.loads(response.content)

    else:
        logger.error(
            'Error in getting email instructions: %s %s',
            response.status_code, response.content)


def request_payout(user_id, amount, description, currency=None):
    context = {
        'user_id': user_id, 'amount': amount, 'description': description,
        'currency': currency, }

    _dragonpay_soap_wrapper('RequestPayout', context)


def request_payout_ex(
        user_name, amount, description, proc_id,
        proc_detail, email, mobile, currency=None):

    context = {
        'user_name': user_name,
        'amount': amount,
        'currency': currency,
        'description': description,
        'processor_id': proc_id,
        'processor_detail': proc_detail,
        'timestamp': datetime.now().isoformat(),
        'email': email,
        'mobile': mobile,
    }

    result = _dragonpay_get_wrapper('RequestPayoutEx', context, payout=True)


def register_payout_user(context):
    # Check that the given context contains the required fields
    payout_context_keys = {
        'address1', 'address2', 'birthdate', 'city', 'country', 'email',
        'first_name', 'last_name', 'middle_name', 'mobile', 'state', 'zip'}

    if not set(context.keys()) == payout_context_keys:
        logger.debug(
            'Keys [%s] are missing from the RegisterPayoutUser context',
            ', '.join(set(context.keys()) - payout_context_keys))

        raise Exception('RegisterPayoutUser context invalid contents')

    result = _dragonpay_get_wrapper('RegisterPayoutUser', context, payout=True)

    return result
