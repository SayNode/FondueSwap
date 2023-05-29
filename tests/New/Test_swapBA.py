import pytest

from brownie import (accounts, 
                    Contract, 
                    MockToken, PoolFactory, Pool, NFT, NFTManager)

@pytest.fixture
def Atoken():
    # fetch the account
    account = accounts[0]

    # deploy contract
    Atoken = MockToken.deploy("TokenA","TA",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Atoken}")

    return Atoken

@pytest.fixture
def Btoken():
    # fetch the account
    account = accounts[0]

    # deploy contract
    Btoken = MockToken.deploy("TokenB","TB",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Btoken}")
    return Btoken

@pytest.fixture
def factoryContract():
    # fetch the account
    account = accounts[0]

    # deploy Staking contract
    factory = UniswapV3Factory.deploy({"from":account})
    # print contract address
    print(f"Factory contract deployed at {factory}")
    return factory

@pytest.fixture
def mintManagerContract(factoryContract):
    # fetch the account
    account = accounts[0]

    # deploy Staking contract
    manager = UniswapV3ManagerMint.deploy(factoryContract, {"from":account})
    # print contract address
    print(f"Mint manager contract deployed at {manager}")
    return manager

@pytest.fixture
def swapManagerContract(factoryContract):
    # fetch the account
    account = accounts[0]

    # deploy Staking contract
    manager = UniswapV3ManagerSwaps.deploy(factoryContract, {"from":account})
    # print contract address
    print(f"Swap manager contract deployed at {manager}")
    return manager

@pytest.fixture
def ABPool(Atoken, Btoken, factoryContract):
    
    # fetch the account
    account = accounts[0]
    
    #Variables
    feeAB=500

    #Create pool AB
    poolCreation = factoryContract.createPool(Atoken, 
                                            Btoken,
                                            feeAB,
                                            {"from": account})
                                            
    poolAB_address = poolCreation.events['PoolCreated']['pool']

    print("Pool Created at ", poolAB_address)

    assert poolAB_address == factoryContract.pools(Atoken, Btoken, 500)

    #Turn pool address into a contract
    poolABI = UniswapV3Pool.abi
    ABPool = Contract.from_abi("UniswapV3Pool", poolAB_address, poolABI)

    #Initial Price
    initP_AB=5000

    #Initialize pool AB
    ABPool.initialize(initP_AB, {"from": account})
    print("Slot0:",ABPool.slot0({"from": account}))
    assert ABPool.slot0({"from": account})[0] != (0)

    return ABPool

@pytest.fixture
def mintPos(Atoken, Btoken, factoryContract, mintManagerContract, ABPool):
# fetch the accounts
    account = accounts[0]

    #Fund the users
    Alice = accounts[1]
    Atoken.mint(Alice, 100000*10**18,{"from": account})
    Btoken.mint(Alice, 1000000*10**18,{"from": account})

    #Set pos
    Atoken.approve(mintManagerContract, 100*10**18, {"from": Alice})
    Btoken.approve(mintManagerContract, 500000*10**18, {"from": Alice})

    mintManagerContract.mint([Atoken, Btoken, 500, 84220, 86130, 100*10**18, 500000*10**18, 0, 0], {"from": Alice} )

    pos = mintManagerContract.getPosition([Atoken, Btoken, 500, Alice, 84220, 86130], {"from": Alice})
    print('Position:',pos)
    assert pos[0]!=0

'''
Tests
'''
def test_inRange(Atoken, Btoken, factoryContract, swapManagerContract, ABPool, mintPos):

    #Fetch the accounts
    account = accounts[0]

    #Fund Bob
    Bob = accounts[2]
    Btoken.mint(Bob, 10000*10**18,{"from": account})

    #Bob wants to swap 1 A token so it approves 1
    Btoken.approve(swapManagerContract, 5000*10**18, {"from": Bob})
    print('Balances before swap:')
    print('Atoken=',int(Atoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('Btoken=',int(Btoken.balanceOf(Bob, {"from": Bob}))/10**18)

    params = [Btoken, Atoken, 500, 5000*10**18, int(int(ABPool.slot0({"from": account})[0])*1.1)]
    tx = swapManagerContract.swapSingle(params, {"from": Bob} )

    print('Balances after swap:')
    print('Atoken=',int(Atoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('Btoken=',int(Btoken.balanceOf(Bob, {"from": Bob}))/10**18)
    