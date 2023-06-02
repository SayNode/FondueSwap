from eth_utils.abi import function_abi_to_4byte_selector, collapse_if_tuple
import json

def encode_custom_error(contract_name, err_name, params):
    with open("build/Contracts/"+contract_name+".json") as f:
        info_json = json.load(f)
    contract_abi = info_json["abi"]
    for error in [abi for abi in contract_abi if abi["type"] == "error"]:
        # Get error signature components
        name = error["name"]
        data_types = [collapse_if_tuple(abi_input) for abi_input in error.get("inputs", [])]
        error_signature_hex = function_abi_to_4byte_selector(error).hex()
 
        if err_name == name:
            encoded_params = ''
            for param in params:
                if(type(param)==str):
                    return('typed error: 0x'+error_signature_hex+param.zfill(66)[2:])
                val = "{0:#0{1}x}".format(param,66)
                val = val[2:]
                encoded_params = encoded_params + val
            return('typed error: 0x'+error_signature_hex+encoded_params)
    
    return 'error not found'