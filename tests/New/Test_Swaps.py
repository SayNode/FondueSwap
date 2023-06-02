import pytest
import brownie
from getError import encode_custom_error
from brownie import (accounts, 
                    Contract, 
                    chain,
                    MockToken, PoolFactory, Pool, NFT, HelpFunctions, SwapManager)

@pytest.fixture
def deployLibrary():
    libDeployer =accounts[9]

    lib = HelpFunctions.deploy({"from":libDeployer})
    # print contract address
    print(f"Lib contract deployed at {lib}")
    return lib

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
    factory = PoolFactory.deploy({"from":account})
    # print contract address
    print(f"Factory contract deployed at {factory}")
    return factory

@pytest.fixture
def swapManagerContract(factoryContract):
    # fetch the account
    account = accounts[0]

    # deploy Staking contract
    swap = SwapManager.deploy(factoryContract,{"from":account})
    # print contract address
    print(f"Swap manager contract deployed at {swap}")
    return swap

@pytest.fixture
def NFTContract(factoryContract, deployLibrary):
    # fetch the account
    account = accounts[0]

    # deploy Staking contract
    nft = NFT.deploy(factoryContract, {"from":account})
    # print contract address
    print(f"NFT contract deployed at {nft}")
    return nft

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
    poolABI = Pool.abi
    ABPool = Contract.from_abi("Pool", poolAB_address, poolABI)

    return ABPool

def set_pos(NFTContract, minter, Atoken, Btoken, fee, lowerTick, upperTick, amountA, amountB):
    #First alice position
    Atoken.approve(NFTContract, amountA, {"from": minter})
    Btoken.approve(NFTContract, amountB, {"from": minter})

    chain.sleep(30)
    pos = NFTContract.mint([minter, Atoken, Btoken, fee, lowerTick, upperTick, amountA, amountB, 0, 0], {"from": minter} )
    chain.sleep(30)
    return pos
    
'''
Tests 
'''
def test_swapAB(Atoken, Btoken, NFTContract, deployLibrary, ABPool,swapManagerContract):
    # fetch the accounts
    account = accounts[0]

    #Fund the users
    Alice = accounts[1]
    Atoken.mint(Alice, 100_000*10**18,{"from": account})
    Btoken.mint(Alice, 100_000*10**18,{"from": account})

    #Variables
    fraq=2**96
    initP_AB=5000

    #Initialize pool AB
    ABPool.initialize(initP_AB, {"from": account})
    print("Slot0:",ABPool.slot0({"from": account}))
    assert ABPool.slot0({"from": account})[0] != (0)
    
    #Alice: First position
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 84220, 86130, 1*10**18, 5000*10**18)

    tokens = NFTContract.totalSupply( {"from": Alice} )
    assert tokens == 1
    print('Total token Supply:',tokens)

    ownedTokens = NFTContract.tokensOfOwner(Alice, {"from": Alice} )
    assert ownedTokens[0] == 0
    assert len(ownedTokens) == 1
    print('Tokens of minter:',ownedTokens)

    pos = NFTContract.tokenIDtoPosition(0, {"from": Alice})
    print('Position:',pos)
    assert pos[0] == ABPool
    assert pos[4] == 84220
    assert pos[5] == 86130


    #Alice: Second position
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 81220, 82130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 87220, 88130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 84520, 85130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 80320, 81230, 1*10**18, 5000*10**18)#bellow range

    tokens = NFTContract.totalSupply( {"from": Alice} )
    assert tokens == 5
    print('Total token Supply:',tokens)

    ownedTokens = NFTContract.tokensOfOwner(Alice, {"from": Alice} )
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (0,1,2,3,4)
    assert len(ownedTokens) == 5

    pos = NFTContract.tokenIDtoPosition(0, {"from": Alice})
    assert pos[0] == ABPool
    assert pos[4] == 84220
    assert pos[5] == 86130
    second_pos = NFTContract.tokenIDtoPosition(1, {"from": Alice})
    assert second_pos[0] == ABPool
    assert second_pos[4] ==81220
    assert second_pos[5] ==82130
    third_pos = NFTContract.tokenIDtoPosition(2, {"from": Alice})
    assert third_pos[0] == ABPool
    assert third_pos[4] == 87220
    assert third_pos[5] == 88130
    fourth_pos = NFTContract.tokenIDtoPosition(3, {"from": Alice})
    assert fourth_pos[0] == ABPool
    assert fourth_pos[4] == 84520
    assert fourth_pos[5] == 85130
    fifth_pos = NFTContract.tokenIDtoPosition(4, {"from": Alice})
    assert fifth_pos[0] == ABPool
    assert fifth_pos[4] == 80320
    assert fifth_pos[5] == 81230

    
