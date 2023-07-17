from thor_requests.contract import Contract
from thor_requests.wallet import Wallet
from thor_requests.connect import Connect
from decouple import config
import time
import pytest


'''
@ Functions
Function to call contract functions (no gas cost)
'''
def call_functions(connector, 
                      _caller,
                      _contract, _contract_address,
                      _name,
                      _params):

    balance_one = connector.call(
            caller=_caller, # fill in your caller address or all zero address
            contract=_contract,
            func_name=_name,
            func_params=_params,
            to=_contract_address,
        )
    print("The function", _name, "from the contract", _contract.get_contract_name(),"was called.")

'''
@ Functions
Function to transact contract functions (has gas cost)
'''
def execute_functions(connector, 
                      _caller,
                      _contract, _contract_address,
                      _name,
                      _params):

    tx = connector.transact(
            _caller,
            contract=_contract,
            func_name=_name,
            func_params=_params,
            to=_contract_address,
    )
    print("The function", _name, "from the contract", _contract.get_contract_name(),"was executed.")

'''
@ Functions
Get wallet balance. This is a separate function just because it is easier
'''
def wallet_balance(connector, token_contract, token_contract_address, _wallet_address, name):

        balance_one = connector.call(
            caller=_wallet_address, # fill in your caller address or all zero address
            contract=token_contract,
            func_name="balanceOf",
            func_params=[_wallet_address],
            to=token_contract_address,
        )
        print(name +" "+ str(_wallet_address)+" balance is: " + str(balance_one["decoded"]["0"]/(10**18)))
        return int(balance_one["decoded"]["0"])




'''
@ Testing Fixtures
Establish the wallets to be used
'''
@pytest.fixture 
def Alice(): #will act as token_holder
    _wallet = Wallet.fromPrivateKey(bytes.fromhex("67bb4fd2be7a00a95fb3571c991dc6982d0e55d7f63910f6a72e2b14d6f9cb33"))
    return _wallet

@pytest.fixture 
def Bob(): #will act as token_receiver
    MNEMONIC = config('MNEMONIC_1')
    _wallet2 = Wallet.fromMnemonic(MNEMONIC.split(', '))
    return _wallet2

@pytest.fixture 
def RandomContract(): #will act as a contract who will call transferFrom to transfer from Alice to Bob
    MNEMONIC = config('MNEMONIC_2')
    _wallet3 = Wallet.fromMnemonic(MNEMONIC.split(', '))
    return _wallet3
    
'''
@ Testing Fixtures
Establish connection to Vechain testnet node
'''
@pytest.fixture
def connector():
    #Connect to node
    connector = Connect("https://testnet.veblocks.net")
    return connector

'''
@ Testing Fixtures
Establish token contract
'''
@pytest.fixture
def token_contract():
    #Get contract
    token_contract = Contract.fromFile("build/contracts/ABI_VET.json")
    return token_contract

@pytest.fixture
def token_contract_address():
    token_contract_address='0x1EA7fA7A4E251B491CAE578dde4E813835ebCa7B'
    return token_contract_address





'''
@ Tests
Test the transferFrom function without the user first giving approval
'''
def test_noapproval(Alice, Bob, RandomContract, connector, token_contract, token_contract_address):

    # Get the balances before the transfer
    print("\n Balances before transfer:")
    send_one = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_one = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    #Attempt to execute the "transferFrom" function
    transferFrom_tx = execute_functions(connector, 
                      RandomContract,
                      token_contract, token_contract_address,
                      "approve",
                      [Alice.getAddress(), Bob.getAddress(), 1*10**18])

    time.sleep(15)

    # Get the balances after the transfer
    print("Balances after transfer:")
    send_two = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_two = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    assert send_one - send_two == 1*10**18
    assert rec_two - rec_one == 1*10**18

'''
@ Tests
Test the transferFrom function with the user first giving approval
'''
def test_withapproval(Alice, Bob, RandomContract, connector, token_contract, token_contract_address):

    # Get the balances before the transfer
    print("\n Balances before transfer:")
    send_one = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_one = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    #Attempt to execute the "approve" function
    approval_tx = execute_functions(connector, 
                      Alice,
                      token_contract, token_contract_address,
                      "approve",
                      [RandomContract.getAddress(), 1*10**18])
    time.sleep(15)

    #Attempt to execute the "transferFrom" function
    transferFrom_tx = execute_functions(connector, 
                      RandomContract,
                      token_contract, token_contract_address,
                      "transferFrom",
                      [Alice.getAddress(), Bob.getAddress(), 1*10**18])
    time.sleep(15)

    # Get the balances after the transfer
    print("Balances after transfer:")
    send_two = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_two = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    assert send_one - send_two == 1*10**18
    assert rec_two - rec_one == 1*10**18

'''
@ Tests
Test the transferFrom function with the user first giving approval, then try to transfer again without
increasing the approved amount
'''
def test_withapproval2times(Alice, Bob, RandomContract, connector, token_contract, token_contract_address):

    # Get the balances before the transfer
    print("\n Balances before transfer:")
    send_one = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_one = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    #Attempt to execute the "approve" function
    approval_tx = execute_functions(connector, 
                      Alice,
                      token_contract, token_contract_address,
                      "approve",
                      [RandomContract.getAddress(), 1*10**18])
    time.sleep(15)

    #Attempt to execute the "transferFrom" function
    transferFrom_tx = execute_functions(connector, 
                      RandomContract,
                      token_contract, token_contract_address,
                      "transferFrom",
                      [Alice.getAddress(), Bob.getAddress(), 1*10**18])
    time.sleep(15)

    #Attempt to execute the "transferFrom" function    
    transferFrom_tx = execute_functions(connector, 
                      RandomContract,
                      token_contract, token_contract_address,
                      "transferFrom",
                      [Alice.getAddress(), Bob.getAddress(), 1*10**18])

    #Get balances after the transfer
    print("Balances after transfer:")
    send_two = wallet_balance(connector, token_contract, token_contract_address, Alice.getAddress(), 'Sender')
    rec_two = wallet_balance(connector, token_contract, token_contract_address, Bob.getAddress(), 'Receiver')

    assert send_one - send_two == 1*10**18
    assert rec_two - rec_one == 1*10**18
