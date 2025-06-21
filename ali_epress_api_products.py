import requests
import hashlib
from GLOBAL_CONST import *
import time

class AliExpressApiProducts:
    def process(self, products):
        appkey = "516068"
        appSecret = "eCMr5mVeMOEOC3mTgagoGa0e3Fw0fkNZ"
        client = iop.IopClient(URL, appkey, appSecret)
        request = iop.IopRequest('aliexpress.ds.product.get')
        request.add_api_param('ship_to_country', 'US')
        request.add_api_param('product_id', '1005003784285827')
        request.add_api_param('target_currency', 'USD')
        request.add_api_param('target_language', 'en')
        request.add_api_param('remove_personal_benefit', 'false')
        request.add_api_param('biz_model', 'biz_model')
        response = client.execute(request, access_token)
        print(response.type)
        print(response.body)
