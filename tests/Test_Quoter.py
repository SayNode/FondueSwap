import pytest
import brownie
import math
from getError import encode_custom_error
from getMultiPoolPath import append_hex
from brownie import (accounts, 
                    Contract, 
                    chain,
                    MockToken, PoolFactory, Quoter, Pool, NFT, HelpFunctions)

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
def Xtoken():
    # fetch the account
    account = accounts[0]

    # deploy contract
    Xtoken = MockToken.deploy("TokenX","TX",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Xtoken}")
    return Xtoken

@pytest.fixture
def Ytoken():
    # fetch the account
    account = accounts[0]

    # deploy contract
    Ytoken = MockToken.deploy("TokenY","TY",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Ytoken}")
    return Ytoken

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
def quoterContract(factoryContract):
    # fetch the account
    account = accounts[0]

    # deploy Quoter contract
    quoter = Quoter.deploy(factoryContract,{"from":account})
    # print contract address
    print(f"Factory contract deployed at {quoter}")
    return quoter

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


@pytest.fixture
def BXPool(Btoken, Xtoken, factoryContract):
    
    # fetch the account
    account = accounts[0]
    
    #Variables
    feeBX=500

    #Create pool AB
    poolCreation = factoryContract.createPool(Btoken, 
                                            Xtoken,
                                            feeBX,
                                            {"from": account})
                                            
    poolBX_address = poolCreation.events['PoolCreated']['pool']

    print("Pool Created at ", poolBX_address)

    assert poolBX_address == factoryContract.pools(Btoken, Xtoken, 500)

    #Turn pool address into a contract
    poolABI = Pool.abi
    BXPool = Contract.from_abi("Pool", poolBX_address, poolABI)

    return BXPool

@pytest.fixture
def XYPool(Xtoken, Ytoken, factoryContract):
    
    # fetch the account
    account = accounts[0]
    
    #Variables
    feeXY=500

    #Create pool XY
    poolCreation = factoryContract.createPool(Xtoken, 
                                            Ytoken,
                                            feeXY,
                                            {"from": account})
                                            
    poolXY_address = poolCreation.events['PoolCreated']['pool']

    print("Pool Created at ", poolXY_address)

    assert poolXY_address == factoryContract.pools(Xtoken, Ytoken, feeXY)

    #Turn pool address into a contract
    poolABI = Pool.abi
    XYPool = Contract.from_abi("Pool", poolXY_address, poolABI)

    return XYPool

def set_pos(NFTContract, minter, Onetoken, Twotoken, fee, lowerTick, upperTick, amountA, amountB):
    #First alice position
    Onetoken.approve(NFTContract, 100000*10**18, {"from": minter})
    Twotoken.approve(NFTContract, 100000*10**18, {"from": minter})

    pos = NFTContract.mint([minter, Onetoken, Twotoken, fee, lowerTick, upperTick, amountA, amountB, 0, 0], {"from": minter} )
    chain.sleep(30)
    return pos

@pytest.fixture
def init_setup_ABPool(Atoken, Btoken, NFTContract, deployLibrary, ABPool):
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

@pytest.fixture 
def init_setup_XYPool(Xtoken, Ytoken, NFTContract, deployLibrary, XYPool):
    # fetch the accounts
    account = accounts[0]

    #Fund the users
    Carol = accounts[8]
    Xtoken.mint(Carol, 100_000*10**18,{"from": account})
    Ytoken.mint(Carol, 100_000*10**18,{"from": account})

    #Variables
    fraq=2**96
    initP_XY=100

    #Initialize pool XY
    XYPool.initialize(initP_XY, {"from": account})
    print("Slot0:",XYPool.slot0({"from": account}))
    assert XYPool.slot0({"from": account})[0] != (0)
    
    #Alice: First position
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 45220, 46130, 1*10**18, 100*10**18)


    #Alice: Second position
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 41220, 42130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 47220, 48130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 44520, 48130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 40320, 41230, 1*10**18, 5000*10**18)#bellow range

@pytest.fixture 
def init_setup_BXPool(Btoken, Xtoken, NFTContract, deployLibrary, BXPool):
    # fetch the accounts
    account = accounts[0]

    #Fund the users
    John = accounts[7]
    Btoken.mint(John, 100_000*10**18,{"from": account})
    Xtoken.mint(John, 100_000*10**18,{"from": account})

    #Variables
    fraq=2**96
    initP_BX=250

    #Initialize pool BX
    BXPool.initialize(initP_BX, {"from": account})
    print("Slot0:",BXPool.slot0({"from": account}))
    assert BXPool.slot0({"from": account})[0] != (0)
    
    #Alice: First position
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 54220, 56130, 1*10**18, 5000*10**18)


    #Alice: Second position
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 51220, 52130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 57220, 58130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 54520, 55130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, John, Btoken, Xtoken,  500, 50320, 51230, 1*10**18, 5000*10**18)#bellow range

   
   
def test_quoter(Atoken, Btoken, ABPool,
                BXPool,
                Xtoken, Ytoken, XYPool,  
                quoterContract,
                NFTContract, deployLibrary,
                init_setup_ABPool, init_setup_XYPool, init_setup_BXPool):
    # fetch the accounts
    account = accounts[0]

    #Fund the users
    Alice = accounts[1]

    #Variables
    fraq=2**96
    initP_AB=5000
    amountIn = 0.01*10**18
    slippage = 0.03

    # Test single pool quoter
    print('\n---------------------------------------------------')
    print('Test single pool quoter')
    # struct QuoteSingleParams {
    #     address tokenIn;
    #     address tokenOut;
    #     uint24 fee;
    #     uint256 amountIn;
    #     uint160 sqrtPriceLimitX96;
    # }

    params=[Atoken.address, Btoken.address, 500, amountIn, int(int(ABPool.slot0({"from": account})[0])*math.sqrt(1-slippage))]
    quotedVals = quoterContract.quoteSingle(params, {"from":account}).return_value
    print('Amount out:',quotedVals[0])
    print('SQRTPriceAfter:',quotedVals[1])
    print('PriceAfter:',(quotedVals[1]/2**96)**2)
    print('Tick after:',quotedVals[2])
    print('Price after:',1.0001**quotedVals[2])


    # Test multiple pool quoter but only one pool
    print('\n---------------------------------------------------')
    print('Test multiple pool quoter but only one pool')
    path = append_hex([Atoken.address, 500, Btoken.address])
    quotedVals = quoterContract.quoteMulti(path, amountIn, {"from":account}).return_value
    print('Amount out:',quotedVals[0])
    print('SQRTPriceAfter:',quotedVals[1])
    print('Price After AB:',(quotedVals[1][0]/2**96)**2)
    print('Tick after:',quotedVals[2])
    print('Price after AB:',1.0001**quotedVals[2][0])


    # Test multiple pool quoter with multiple pools
    print('\n---------------------------------------------------')
    print('Test multiple pool quoter with multiple pools')
    print('Price before AB:', (int(int(ABPool.slot0({"from": account})[0]))/2**96)**2)
    print('Price before BX:', (int(int(BXPool.slot0({"from": account})[0]))/2**96)**2)
    print('Price before XY:', (int(int(XYPool.slot0({"from": account})[0]))/2**96)**2)
    amountIn = 0.00001*10**18
    path = append_hex([Atoken.address, 500, Btoken.address, 500, Xtoken.address, 500, Ytoken.address])
    quotedVals = quoterContract.quoteMulti(path, amountIn, {"from":account}).return_value
    print('Amount out:',quotedVals[0]/10**18)
    print('SQRTPriceAfter:',quotedVals[1])
    print('Price After AB:',(quotedVals[1][0]/2**96)**2)
    print('Price After BX:',(quotedVals[1][1]/2**96)**2)
    print('Price After XY:',(quotedVals[1][2]/2**96)**2)
    print('Tick after:',quotedVals[2])
    print('Price after AB:',1.0001**quotedVals[2][0])
    print('Price after BX:',1.0001**quotedVals[2][1])
    print('Price after XY:',1.0001**quotedVals[2][2])