import pytest
import math
import brownie
from getError import encode_custom_error
from brownie import (accounts, 
                    Contract, 
                    chain,
                    MockToken, PoolFactory, Pool, NFT, HelpFunctions)

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
    
@pytest.fixture
def settingPositions(Atoken, Btoken, NFTContract, deployLibrary, ABPool):
    # fetch the accounts
    account = accounts[0]

    #Fund the users
    Alice = accounts[1]
    Bob = accounts[2]
    Atoken.mint(Alice, 100_000*10**18,{"from": account})
    Btoken.mint(Alice, 100_000*10**18,{"from": account})
    Atoken.mint(Bob, 100_000*10**18,{"from": account})
    Btoken.mint(Bob, 100_000*10**18,{"from": account})

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

    #Bob: First position
    set_pos(NFTContract, Bob, Atoken, Btoken, 500, 83220, 86130, 1*10**18, 5000*10**18)
    sixth_pos = NFTContract.tokenIDtoPosition(5, {"from": Alice})
    assert sixth_pos[0] == ABPool
    assert sixth_pos[4] == 83220
    assert sixth_pos[5] == 86130

    
    BobOwnedTokens = NFTContract.tokensOfOwner(Bob, {"from": Bob} )
    print('Tokens of Bob:',BobOwnedTokens)
    assert BobOwnedTokens == (5,)
    assert len(BobOwnedTokens) == 1

def remLiq(ABPool, NFTContract, minter, tokenID):

    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})

    liquidity =  pos[1]
    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    NFTContract.removeLiquidity([tokenID, liquidity],{"from": minter})
    chain.sleep(30)
    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})

    currentPrice = (ABPool.slot0()[0]/(2**96))**2
    currentTick = math.log(currentPrice,1.0001)
    assert pos[0] == ABPool
    assert pos[1] == 0
    if(lowerTick<=currentTick and upperTick>=currentTick):
        assert pos[2] != tokensOwed0
        assert pos[3] != tokensOwed1
    elif (lowerTick>=currentTick and upperTick>=currentTick):
        assert pos[2] != tokensOwed0
        assert pos[3] == tokensOwed1
    elif (lowerTick<=currentTick and upperTick<=currentTick ):
        assert pos[2] == tokensOwed0
        assert pos[3] != tokensOwed1
    assert pos[4] == lowerTick
    assert pos[5] == upperTick

def addLiq(Atoken, Btoken, NFTContract, amountA,amountB, minter, tokenID):
    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})

    liquidity =  pos[1]
    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    Atoken.approve(NFTContract, amountA, {"from": minter})
    Btoken.approve(NFTContract, amountB, {"from": minter})
    NFTContract.addLiquidity([tokenID, amountA, amountB, 0, 0],{"from": minter})

    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})
    assert pos[1] > liquidity
    assert pos[2:] == (tokensOwed0, tokensOwed1, lowerTick, upperTick)

def collectLiq(ABPool, NFTContract, minter, tokenID):

    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})

    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    NFTContract.collect([tokenID, tokensOwed0, tokensOwed1],{"from":minter})
    chain.sleep(30)
    pos = NFTContract.tokenIDtoPosition(tokenID, {"from": minter})
    assert pos[0] == ABPool
    assert pos[1] == 0
    assert pos[2] == 0
    assert pos[3] == 0
    assert pos[4] == lowerTick
    assert pos[5] == upperTick
'''
Test
'''
def test_updatePositions(Atoken, Btoken, NFTContract, deployLibrary, ABPool, settingPositions):

    Alice = accounts[1]
    Bob =accounts[2]

    #Should revert the burn because the position is not cleared
    with brownie.reverts(encode_custom_error('NFT', 'PositionNotCleared', '')):
        NFTContract.burn(0,{"from": Alice})

    #Should revert the burn because Alice does not own this token
    with brownie.reverts(encode_custom_error('NFT', 'NotAuthorized', '')):
        NFTContract.burn(5,{"from": Alice})

    #Add extra liquidity to Position 0
    addLiq(Atoken, Btoken, NFTContract, 0.02e18, 100e18, Alice, 0)
 
    #Should revert the remove liquidity because Alice does not own this token
    with brownie.reverts(encode_custom_error('NFT', 'NotAuthorized', '')):
        remLiq(ABPool,NFTContract, Alice, 5)

    #Remove all liquidity from Position 0
    remLiq(ABPool,NFTContract, Alice, 0)

    #Should revert the burn because the position is not cleared
    with brownie.reverts(encode_custom_error('NFT', 'PositionNotCleared', '')):
        NFTContract.burn(0,{"from": Alice})

    #Should revert the collect because Alice does not own this token
    with brownie.reverts(encode_custom_error('NFT', 'NotAuthorized', '')):
        collectLiq(ABPool, NFTContract, Alice, 5)

    #Collect tokens from Position 0
    collectLiq(ABPool, NFTContract, Alice, 0)

    #Burn token 0 position
    NFTContract.burn(0,{"from": Alice})

    tokens = NFTContract.totalSupply( {"from": Alice} )
    assert tokens == 5
    print('Total token Supply:',tokens)

    ownedTokens = NFTContract.tokensOfOwner(Alice, {"from": Alice} )
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (1,2,3,4)
    assert len(ownedTokens) == 4

    
    BobOwnedTokens = NFTContract.tokensOfOwner(Bob, {"from": Bob} )
    print('Tokens of Bob:',BobOwnedTokens)
    assert BobOwnedTokens == (5,)
    assert len(BobOwnedTokens) == 1

    #Burn token 2 position
    #remove all liquidity from Position 2
    remLiq(ABPool,NFTContract, Alice, 2)

    #collect tokens from Position 2
    collectLiq(ABPool, NFTContract, Alice, 2)
    NFTContract.burn(2,{"from": Alice})

    tokens = NFTContract.totalSupply( {"from": Alice} )
    assert tokens == 4
    print('Total token Supply:',tokens)

    ownedTokens = NFTContract.tokensOfOwner(Alice, {"from": Alice} )
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (1,3,4)
    assert len(ownedTokens) == 3

    BobOwnedTokens = NFTContract.tokensOfOwner(Bob, {"from": Bob} )
    print('Tokens of Bob:',BobOwnedTokens)
    assert BobOwnedTokens == (5,)
    assert len(BobOwnedTokens) == 1

    # Burn token 5
    #remove all liquidity from Position 5
    remLiq(ABPool,NFTContract, Bob, 5)

    #collect tokens from Position 5
    collectLiq(ABPool, NFTContract, Bob, 5)
    NFTContract.burn(5,{"from": Bob})

    BobOwnedTokens = NFTContract.tokensOfOwner(Bob, {"from": Bob} )
    print('Tokens of Bob:',BobOwnedTokens)
    assert BobOwnedTokens == ()
    assert len(BobOwnedTokens) == 0