from thor_requests.connect import Connect
from thor_requests.wallet import Wallet
from thor_requests.contract import Contract
from decouple import config
import json
import time

#Connect to Vechain node API
_connector = Connect("https://testnet.veblocks.net")

# Import wallets from mnemonic
MNEMONIC = config('MNEMONIC_1')
_wallet = Wallet.fromMnemonic(MNEMONIC.split(', '))

# library_byte = '9828dc171e405abf5282769f90461a6e284fa583'
myWalletAddress = '0x5959D60345aB12befE24bd8d21EF53eBa7688f6D'
saynodeWalletAddress = '0x6620086742791009C5348d35aa5bD2018CAb5FF7'

#Library
_contract_lib = Contract.fromFile("./build/contracts/HelpFunctions.json")
TX_HASH = _connector.deploy(_wallet, _contract_lib, [], [])
time.sleep(30)
_libAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Library contract deployed at", _libAddress)
library_byte = _libAddress[2:].lower()

deploy_list = ['PoolFactory', 'NFT', 'Quoter', 'SwapManager']
for contract_name in deploy_list:
    with open("./build/contracts/"+contract_name+".json", "r") as f:
        abi = json.load(f)
        
        if(abi["bytecode"].find('__HelpFunctions_________________________')!=-1):
            if(len(abi["bytecode"]) == 
            len(abi["bytecode"].replace('__HelpFunctions_________________________',library_byte))):
                abi["bytecode"] = abi["bytecode"].replace('__HelpFunctions_________________________',library_byte)
                with open("./build/contracts/"+contract_name+".json", 'w') as outfile:
                    json.dump(abi, outfile)

#Pool Factory
_contract_PoolFactory = Contract.fromFile("./build/contracts/PoolFactory.json")
TX_HASH = _connector.deploy(_wallet, _contract_PoolFactory, [], [])
time.sleep(30)
_factoryAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Pool Factory contract deployed at", _factoryAddress)

# #NFT
_contract_NFT = Contract.fromFile("./build/contracts/NFT.json")
TX_HASH = _connector.deploy(_wallet, _contract_NFT, ["address"], [_factoryAddress])
time.sleep(30)
_NFTAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("NFT contract deployed at", _NFTAddress)

#Quoter
_contract_Quoter = Contract.fromFile("./build/contracts/Quoter.json")
TX_HASH = _connector.deploy(_wallet, _contract_Quoter, ["address"], [_factoryAddress])
time.sleep(30)
_QuoterAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Quoter contract deployed at", _QuoterAddress)


# #Swap Manager
_contract_SwapManager = Contract.fromFile("./build/contracts/SwapManager.json")
TX_HASH = _connector.deploy(_wallet, _contract_SwapManager, ["address"], [_factoryAddress])
time.sleep(30)
_SwapManagerAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Swap Manager contract deployed at", _SwapManagerAddress)

#TokenX
_contract_TokenX = Contract.fromFile("./build/contracts/MockToken.json")
TX_HASH = _connector.deploy(_wallet, _contract_TokenX, ["address", "address"], [myWalletAddress, saynodeWalletAddress])
time.sleep(30)
_TokenXAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Token X contract deployed at", _TokenXAddress)

#TokenY
_contract_TokenY = Contract.fromFile("./build/contracts/MockToken.json")
TX_HASH = _connector.deploy(_wallet, _contract_TokenY, ["address", "address"], [myWalletAddress, saynodeWalletAddress])
time.sleep(30)
_TokenYAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Token Y contract deployed at", _TokenYAddress)

#TokenA
_contract_TokenA = Contract.fromFile("./build/contracts/MockToken.json")
TX_HASH = _connector.deploy(_wallet, _contract_TokenA, ["address", "address"], [myWalletAddress, saynodeWalletAddress])
time.sleep(30)
_TokenAAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Token A contract deployed at", _TokenAAddress)

#TokenB
_contract_TokenB = Contract.fromFile("./build/contracts/MockToken.json")
TX_HASH = _connector.deploy(_wallet, _contract_TokenB, ["address", "address"], [myWalletAddress, saynodeWalletAddress])
time.sleep(30)
_TokenBAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['contractAddress']
print("Token B contract deployed at", _TokenBAddress)

# '''
# Test deployed contracts
# '''
#Check Initial Balances
init_balance_X = _connector.call(myWalletAddress, 
                                _contract_TokenX, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenXAddress)
init_balance_Y = _connector.call(myWalletAddress, 
                                _contract_TokenY, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenYAddress)
print('\n Initial balance X', init_balance_X)
print('\n Initial balance Y', init_balance_Y)

#Pool Factory
TX_HASH = _connector.transact(_wallet, 
                                _contract_PoolFactory, 
                                "createPool", 
                                [_TokenXAddress, _TokenYAddress, 500], 
                                _factoryAddress)
time.sleep(30)
XYPoolAddress = _connector.get_tx_receipt(TX_HASH['id'])['outputs'][0]['events'][0]['address']
print('xyPool', XYPoolAddress)
TX_HASH = _connector.call(myWalletAddress, 
                                _contract_PoolFactory, 
                                "getCreatedPools", 
                                [], 
                                _factoryAddress)
time.sleep(30)
print('\n Arrays',TX_HASH['decoded'])

TX_HASH = _connector.call(myWalletAddress, 
                                _contract_PoolFactory, 
                                "pools", 
                                [_TokenXAddress, _TokenYAddress, 500], 
                                _factoryAddress)
time.sleep(30)
print('\n Pool fetched',TX_HASH['decoded'])
#Initialise pool
_contract_Pool = Contract.fromFile("./build/contracts/Pool.json")
TX_HASH = _connector.transact(_wallet, 
                                _contract_Pool, 
                                "initialize", 
                                [5000], 
                                XYPoolAddress)
time.sleep(30)
res = _connector.get_tx_receipt(TX_HASH['id'])
print('\n Initialize: \n', res)

# Mint Position
TX_HASH = _connector.call(myWalletAddress, 
                                _contract_Pool, 
                                "slot0", 
                                [], 
                                XYPoolAddress)
print('\n S0: \n',TX_HASH)
TX_HASH = _connector.transact(_wallet, 
                                _contract_TokenX, 
                                "approve", 
                                [_NFTAddress, 1000000000000000000], 
                                _TokenXAddress)
TX_HASH = _connector.transact(_wallet, 
                                _contract_TokenY, 
                                "approve", 
                                [_NFTAddress, 5000000000000000000000], 
                                _TokenYAddress)
lowerTick = 84220
upperTick = 86130
time.sleep(40)
allowanceX = _connector.call(myWalletAddress, 
                                _contract_TokenX, 
                                "allowance", 
                                [myWalletAddress, _NFTAddress], 
                                _TokenXAddress)
allowanceY = _connector.call(myWalletAddress, 
                                _contract_TokenY, 
                                "allowance", 
                                [myWalletAddress, _NFTAddress], 
                                _TokenYAddress)
print('\n AllowanceX:',allowanceX)
print('\n AllowanceY:',allowanceY)
time.sleep(20)
mintTX = _connector.transact(_wallet, 
                                _contract_NFT, 
                                "mint", 
                                [myWalletAddress,
                                 _TokenXAddress,
                                 _TokenYAddress,
                                 500,
                                 lowerTick,
                                 upperTick,
                                 1000000000000000000, 
                                 5000000000000000000000,
                                 0,
                                 0], 
                                _NFTAddress)
time.sleep(30)
print('\n Mint: \n',_connector.get_tx_receipt(mintTX['id']))
#Check Balance After Mint
init_balance_X = _connector.call(myWalletAddress, 
                                _contract_TokenX, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenXAddress)
init_balance_Y = _connector.call(myWalletAddress, 
                                _contract_TokenY, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenYAddress)
print('\n Balance X After Mint', init_balance_X)
print('\n  Balance Y After Mint', init_balance_Y)
#----------------------------------------------------------------------------

# _NFTAddress = '0x722b131da9e345b0687a60613ca53ef4fa80c3a2'
# _QuoterAddress = '0xb6d2a2b230c00aa1e7706f369da6cd82866220e5'
# _TokenXAddress = '0xae945928710e4e062de32066eca3e32a07875f7a'
# _TokenYAddress =  '0x11ee62273ecd143e4dcb84dd8e3478c8e2bd5ac7'
# _TokenAAddress = '0x50fd19257fd5f8bef1be2f419c44b2f92dd54860'
# _TokenBAddress = '0x1a0910dba1701d920e0366ac894ccff1488a074d'
# xyPool = '0x6949ce54150e33f3f8656521af0e64619c36a361'

#Swap
TX_HASH = _connector.transact(_wallet, 
                                _contract_TokenX, 
                                "approve", 
                                [_SwapManagerAddress, 1000000000000000000], 
                                _TokenXAddress)
time.sleep(30)
swapTX = _connector.transact(_wallet, 
                            _contract_SwapManager, 
                            "swapSingle", 
                            [_TokenXAddress,
                             _TokenYAddress,
                             500,
                             100000,
                             0], 
                            _SwapManagerAddress)
time.sleep(30)
print('\n Swap: \n',_connector.get_tx_receipt(swapTX['id']))
#Quoter
quoterTX = _connector.transact(_wallet, 
                            _contract_Quoter, 
                            "quoteSingle", 
                            [_TokenXAddress,
                             _TokenYAddress,
                             500,
                             100000,
                             0], 
                            _QuoterAddress)
time.sleep(30)
print('\n Quoter: \n',_connector.get_tx_receipt(quoterTX['id']))

#Check Balance After Swap
init_balance_X = _connector.call(myWalletAddress, 
                                _contract_TokenX, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenXAddress)
init_balance_Y = _connector.call(myWalletAddress, 
                                _contract_TokenY, 
                                "balanceOf", 
                                [myWalletAddress], 
                                _TokenYAddress)
print('\n Balance X After Swap', init_balance_X)
print('\n  Balance Y After Swap', init_balance_Y)


# # __HelpFunctions_________________________
# 9828dc171E405aBf5282769F90461a6E284fA583
# forge create --rpc-url "https://testnet.veblocks.net" --mnemonic "next, impact, head, harbor, cupboard, amateur, design, alley, hamster, already, trash, crumble" <your_private_key> src/Quoter.sol:Quoter

amounts = _connector.call(myWalletAddress, 
                                _contract_NFT, 
                                "userToAllPositionsTwo", 
                                [myWalletAddress], 
                                _NFTAddress)
print(amounts)