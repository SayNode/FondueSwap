import pytest
import brownie
from getError import encode_custom_error
from getMultiPoolPath import append_hex
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
def init_setup_ABPool(Atoken, Btoken, NFTContract, deployLibrary, ABPool,swapManagerContract):
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

@pytest.fixture #METER TICKS CORRECTS DE POSIÇÃO!!!!!!!!!11
def init_setup_XYPool(Xtoken, Ytoken, NFTContract, deployLibrary, XYPool,swapManagerContract):
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

    # tokens = NFTContract.totalSupply( {"from": Carol} )
    # assert tokens == 6
    # print('Total token Supply:',tokens)

    # ownedTokens = NFTContract.tokensOfOwner(Carol, {"from": Carol} )
    # assert ownedTokens[0] == 0
    # assert len(ownedTokens) == 1
    # print('Tokens of minter:',ownedTokens)

    # pos = NFTContract.tokenIDtoPosition(0, {"from": Carol})
    # print('Position:',pos)
    # assert pos[0] == XYPool
    # assert pos[4] == 45220
    # assert pos[5] == 46130


    #Alice: Second position
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 41220, 42130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 47220, 48130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 44520, 48130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 40320, 41230, 1*10**18, 5000*10**18)#bellow range

    # tokens = NFTContract.totalSupply( {"from": Carol} )
    # assert tokens == 5
    # print('Total token Supply:',tokens)

    # ownedTokens = NFTContract.tokensOfOwner(Carol, {"from": Carol} )
    # print('Tokens of Carol:',ownedTokens)
    # assert ownedTokens == (0,1,2,3,4)
    # assert len(ownedTokens) == 5

    # pos = NFTContract.tokenIDtoPosition(0, {"from": Carol})
    # assert pos[0] == XYPool
    # assert pos[4] == 45220
    # assert pos[5] == 46130
    # second_pos = NFTContract.tokenIDtoPosition(1, {"from": Carol})
    # assert second_pos[0] == XYPool
    # assert second_pos[4] ==41220
    # assert second_pos[5] ==42130
    # third_pos = NFTContract.tokenIDtoPosition(2, {"from": Carol})
    # assert third_pos[0] == XYPool
    # assert third_pos[4] == 47220
    # assert third_pos[5] == 48130
    # fourth_pos = NFTContract.tokenIDtoPosition(3, {"from": Carol})
    # assert fourth_pos[0] == XYPool
    # assert fourth_pos[4] == 44520
    # assert fourth_pos[5] == 48130
    # fifth_pos = NFTContract.tokenIDtoPosition(4, {"from": Carol})
    # assert fifth_pos[0] == XYPool
    # assert fifth_pos[4] == 40320
    # assert fifth_pos[5] == 41230

@pytest.fixture #METER TICKS CORRECTS DE POSIÇÃO!!!!!!!!!11
def init_setup_BXPool(Btoken, Xtoken, NFTContract, deployLibrary, BXPool,swapManagerContract):
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

    # tokens = NFTContract.totalSupply( {"from": John} )
    # assert tokens == 1
    # print('Total token Supply:',tokens)

    # ownedTokens = NFTContract.tokensOfOwner(John, {"from": John} )
    # assert ownedTokens[0] == 0
    # assert len(ownedTokens) == 1
    # print('Tokens of minter:',ownedTokens)

    # pos = NFTContract.tokenIDtoPosition(0, {"from": John})
    # print('Position:',pos)
    # assert pos[0] == BXPool
    # assert pos[4] == 54220
    # assert pos[5] == 56130


    #Alice: Second position
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 51220, 52130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 57220, 58130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, John, Btoken, Xtoken, 500, 54520, 55130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, John, Btoken, Xtoken,  500, 50320, 51230, 1*10**18, 5000*10**18)#bellow range

    # tokens = NFTContract.totalSupply( {"from": John} )
    # assert tokens == 5
    # print('Total token Supply:',tokens)

    # ownedTokens = NFTContract.tokensOfOwner(John, {"from": John} )
    # print('Tokens of Carol:',ownedTokens)
    # assert ownedTokens == (0,1,2,3,4)
    # assert len(ownedTokens) == 5

    # pos = NFTContract.tokenIDtoPosition(0, {"from": John})
    # assert pos[0] == BXPool
    # assert pos[4] == 54220
    # assert pos[5] == 56130
    # second_pos = NFTContract.tokenIDtoPosition(1, {"from": John})
    # assert second_pos[0] == BXPool
    # assert second_pos[4] ==51220
    # assert second_pos[5] ==52130
    # third_pos = NFTContract.tokenIDtoPosition(2, {"from": John})
    # assert third_pos[0] == BXPool
    # assert third_pos[4] == 57220
    # assert third_pos[5] == 58130
    # fourth_pos = NFTContract.tokenIDtoPosition(3, {"from": John})
    # assert fourth_pos[0] == BXPool
    # assert fourth_pos[4] == 54520
    # assert fourth_pos[5] == 55130
    # fifth_pos = NFTContract.tokenIDtoPosition(4, {"from": John})
    # assert fifth_pos[0] == BXPool
    # assert fifth_pos[4] == 50320
    # assert fifth_pos[5] == 51230


def test_MultipleSwapAB(Atoken, Btoken, ABPool,
                BXPool,
                Xtoken, Ytoken, XYPool,  
                NFTContract, deployLibrary, swapManagerContract, 
                init_setup_ABPool, init_setup_XYPool, init_setup_BXPool):
    
    # fetch the accounts
    account = accounts[0]

    #Establish the users
    Alice = accounts[1]
    Bob = accounts[2]
    Carol =accounts[8]

    #Funding the users
    Atoken.mint(Bob, 10_000*10**18,{"from": account})

    #Check initial balances
    init_Alice_balance_tokenA = Atoken.balanceOf(Alice)
    init_Bob_balance_tokenA = Atoken.balanceOf(Bob)
    init_Carol_balance_tokenA = Atoken.balanceOf(Carol)
    init_Alice_balance_tokenB = Btoken.balanceOf(Alice)
    init_Bob_balance_tokenB = Btoken.balanceOf(Bob)
    init_Carol_balance_tokenB = Btoken.balanceOf(Carol)
    init_Bob_balance_tokenY=Ytoken.balanceOf(Bob)

    #Check swap correctness
    Atoken.approve(swapManagerContract, 10*10**18, {"from": Bob})
    slippage = 0.03
    path = append_hex([Atoken.address, 500, Btoken.address, 500, Xtoken.address, 500, Ytoken.address])

    # struct SwapParams {
    #     bytes path;
    #     address recipient;
    #     uint256 amountIn;
    #     uint256 minAmountOut;
    # }
    SwapParams = [path, Bob, 0.00001*10**18, (0.00001*10**18)*(1-slippage)]
    swapManagerContract.swap(SwapParams, {"from": Bob} )

    print(init_Bob_balance_tokenA)
    print(Atoken.balanceOf(Bob))
    print(init_Bob_balance_tokenY)
    print(Ytoken.balanceOf(Bob))
    assert Atoken.balanceOf(Bob)<init_Bob_balance_tokenA
    assert Ytoken.balanceOf(Bob)>init_Bob_balance_tokenY

    #Check if Alice gets the correct rewards after withdrawing her position