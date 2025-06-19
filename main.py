import json
from ali_epress_api import AliExpressApi

if __name__ == "__main__":
    api = AliExpressApi()
    result = AliExpressApi().process()
    print(json.dumps(result, indent=4, ensure_ascii=False))
