from thor_requests.contract import Contract
from thor_requests.wallet import Wallet
from thor_requests.connect import Connect
from decouple import config
from testFunctions import call_functions, execute_functions, wallet_balance
from getError import encode_custom_error
from getMultiPoolPath import append_hex
import pytest
import math

'''
@ Testing Fixtures
Establish the wallets to be used
'''
@pytest.fixture 
def Alice():
    _wallet = Wallet.fromPrivateKey(bytes.fromhex("67bb4fd2be7a00a95fb3571c991dc6982d0e55d7f63910f6a72e2b14d6f9cb33"))
    return _wallet

@pytest.fixture 
def Bob(): 
    MNEMONIC = config('MNEMONIC_1')
    _wallet2 = Wallet.fromMnemonic(MNEMONIC.split(', '))
    return _wallet2

@pytest.fixture 
def Carol():
    return Wallet.newWallet()

@pytest.fixture 
def deployer(): #will act as a contract who will call transferFrom to transfer from Alice to Bob
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

@pytest.fixture
def deployLibrary(deployer, connector):
    libDeployer = deployer

    _contract = Contract.fromFile("./build/contracts/HelpFunctions.json")
    lib = connector.deploy(libDeployer, _contract)
    # print contract address
    print(f"Lib contract deployed at {lib}")
    return lib

@pytest.fixture
def Atoken(deployer, connector):
    # fetch the account
    account = deployer

    _contract = Contract.fromFile("./build/contracts/MockToken.json")

    Atoken = connector.deploy(account, _contract,["string", "string", "uint8"],["TokenA","TA",18])
    # print contract address
    print(f"Token contract deployed at {Atoken}")

    return Atoken

@pytest.fixture
def Btoken(deployer, connector):
    # fetch the account
    account = deployer

    _contract = Contract.fromFile("./build/contracts/MockToken.json")

    Btoken = connector.deploy(account, _contract,["string", "string", "uint8"],["TokenB","TB",18])
    # print contract address
    print(f"Token contract deployed at {Btoken}")
    return Btoken

@pytest.fixture
def Xtoken(deployer, connector):
    account = deployer

    _contract = Contract.fromFile("./build/contracts/MockToken.json")

    Xtoken = connector.deploy(account, _contract,["string", "string", "uint8"],["TokenX","TX",18])
    # print contract address
    print(f"Token contract deployed at {Xtoken}")
    return Xtoken

@pytest.fixture
def Ytoken(deployer, connector):

    account = deployer

    _contract = Contract.fromFile("./build/contracts/MockToken.json")

    Ytoken = connector.deploy(account, _contract,["string", "string", "uint8"],["TokenY","TY",18])
    # print contract address
    print(f"Token contract deployed at {Ytoken}")
    return Ytoken

@pytest.fixture
def factoryContract(deployer, connector):
    # fetch the account
    account = deployer
    
    _contract = Contract.fromFile("./build/contracts/PoolFactory.json")

    factory = connector.deploy(account, _contract)
    # print contract address
    print(f"Factory contract deployed at {factory}")
    return factory

@pytest.fixture
def swapManagerContract(deployer, connector, 
                        factoryContract):
    # fetch the account
    account = deployer
    
    _contract = Contract.fromFile("./build/contracts/SwapManager.json")

    swap = connector.deploy(account, _contract, ["address"], [factoryContract])

    # print contract address
    print(f"Swap manager contract deployed at {swap}")
    return swap

@pytest.fixture
def NFTContract(deployer, connector, 
                factoryContract, deployLibrary):
    # fetch the account
    account = deployer
    
    _contract = Contract.fromFile("./build/contracts/NFT.json")

    nft = connector.deploy(account, _contract, ["address"], [factoryContract])

    # print contract address
    print(f"NFT contract deployed at {nft}")
    return nft

@pytest.fixture
def ABPool(deployer, connector, 
           Atoken, Btoken, 
           factoryContract):
    
    # fetch the account
    account = deployer
    
    #Variables
    feeAB=500

    #Create pool AB
    poolCreation = execute_functions(connector, 
                      account,
                      factoryContract, factoryContract.address,
                      "createPool",
                      [Atoken, Btoken, feeAB])

                                            
    poolAB_address = poolCreation.events['PoolCreated']['pool']

    print("Pool Created at ", poolAB_address)

    assert poolAB_address == call_functions(connector, 
                      account,
                      factoryContract, factoryContract.address,
                      "pools",
                      [Atoken, Btoken, feeAB])

    #Turn pool address into a contract
    abPool={}
    abPool["abi"] = Contract.fromFile("./build/contracts/Pool.json")
    abPool["address"]= poolAB_address

    return abPool


@pytest.fixture
def XYPool(deployer, connector,
           Xtoken, Ytoken, factoryContract):
    
    # fetch the account
    account = deployer
    
    #Variables
    feeXY=500

    #Create pool AB
    poolCreation = execute_functions(connector, 
                      account,
                      factoryContract, factoryContract.address,
                      "createPool",
                      [Xtoken, Ytoken, feeXY])

                                            
    poolXY_address = poolCreation.events['PoolCreated']['pool']

    print("Pool Created at ", poolXY_address)

    assert poolXY_address == call_functions(connector, 
                      account,
                      factoryContract, factoryContract.address,
                      "pools",
                      [Xtoken, Ytoken, feeXY])

    #Turn pool address into a contract
    xyPool={}
    xyPool["abi"] = Contract.fromFile("./build/contracts/Pool.json")
    xyPool["address"]= poolXY_address

    return xyPool

def set_pos(connector, NFTContract, minter, Onetoken, Twotoken, fee, lowerTick, upperTick, amountA, amountB):
    #First alice position
    # approve
    execute_functions(connector, 
                      minter,
                      Onetoken, Onetoken.address,
                      "approve",
                      [NFTContract, 100000*10**18])
    execute_functions(connector, 
                      minter,
                      Twotoken, Twotoken.address,
                      "approve",
                      [NFTContract, 100000*10**18])
    # set position
    pos = execute_functions(connector, 
                      minter,
                      NFTContract, NFTContract.address,
                      "mint",
                      [[minter, Onetoken, Twotoken, fee, lowerTick, upperTick, amountA, amountB, 0, 0]])
    
    return pos
    
@pytest.fixture
def init_setup_ABPool(connector, Alice, deployer, Atoken, Btoken, NFTContract, deployLibrary, ABPool,swapManagerContract):
    # fetch the accounts
    account = deployer
    Alice = Alice

    #Fund Alice
    execute_functions(connector, 
                        deployer,
                        Atoken, Atoken.address,
                        "mint",
                        [Alice, 100_000*10**18])
    execute_functions(connector, 
                        deployer,
                        Btoken, Btoken.address,
                        "mint",
                        [Alice, 100_000*10**18])

    #Variables
    fraq=2**96
    initP_AB=5000

    #Initialize pool AB
    tx = execute_functions(connector, 
                        deployer,
                        ABPool, ABPool.address,
                        "initialize",
                        [initP_AB])
    slot_zero = call_functions(connector, 
                        deployer,
                        ABPool, ABPool.address,
                        "slot0",
                        [])
    print("Slot0:",slot_zero)
    assert slot_zero[0] != (0)
    
    #Alice: First position
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 84220, 86130, 1*10**18, 5000*10**18)

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 1
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Alice])

    assert ownedTokens[0] == 0
    assert len(ownedTokens) == 1
    print('Tokens of minter:',ownedTokens)

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [0])

    print('Position:',pos)
    assert pos[0] == ABPool
    assert pos[4] == 84220
    assert pos[5] == 86130


    #Alice: Second position
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 81220, 82130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 87220, 88130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 84520, 85130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 80320, 81230, 1*10**18, 5000*10**18)#bellow range

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 5
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Alice])
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (0,1,2,3,4)
    assert len(ownedTokens) == 5

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [0])
    assert pos[0] == ABPool
    assert pos[4] == 84220
    assert pos[5] == 86130
    second_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [1])
    assert second_pos[0] == ABPool
    assert second_pos[4] ==81220
    assert second_pos[5] ==82130
    third_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [2])
    assert third_pos[0] == ABPool
    assert third_pos[4] == 87220
    assert third_pos[5] == 88130
    fourth_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [3])
    assert fourth_pos[0] == ABPool
    assert fourth_pos[4] == 84520
    assert fourth_pos[5] == 85130
    fifth_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [4])
    assert fifth_pos[0] == ABPool
    assert fifth_pos[4] == 80320
    assert fifth_pos[5] == 81230

@pytest.fixture 
def init_setup_XYPool(connector, deployer, Carol, Xtoken, Ytoken, NFTContract, deployLibrary, XYPool,ABPool, swapManagerContract):

    #Fund Carol
    execute_functions(connector, 
                        deployer,
                        Xtoken, Xtoken.address,
                        "mint",
                        [Carol, 100_000*10**18])
    execute_functions(connector, 
                        deployer,
                        Ytoken, Ytoken.address,
                        "mint",
                        [Carol, 100_000*10**18])

    #Variables
    fraq=2**96
    initP_XY=100

    #Initialize pool XY
    tx = execute_functions(connector, 
                        deployer,
                        XYPool, XYPool.address,
                        "initialize",
                        [initP_XY])
    slot_zero = call_functions(connector, 
                        deployer,
                        XYPool, XYPool.address,
                        "slot0",
                        [])
    print("Slot0:",slot_zero)
    assert slot_zero[0] != (0)
    
    #Alice: First position
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 45220, 46130, 1*10**18, 100*10**18)

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])

    assert tokens == 6
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Carol])
    assert ownedTokens[0] == 5
    assert len(ownedTokens) == 1
    print('Tokens of minter:',ownedTokens)

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [5])
    print('Position:',pos)
    print(ABPool)
    assert pos[0] == XYPool
    assert pos[4] == 45220
    assert pos[5] == 46130


    #Alice: Second position
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 41220, 42130, 0.1*10**18, 500*10**18)# bellow range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 47220, 48130, 0.1*10**18, 500*10**18)#above range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 44520, 48130, 0.01*10**18, 50*10**18)#within range
    set_pos(NFTContract, Carol, Xtoken, Ytoken, 500, 40320, 41230, 1*10**18, 5000*10**18)#bellow range

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 10
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Carol])
    print('Tokens of Carol:',ownedTokens)
    assert ownedTokens == (5,6,7,8,9)
    assert len(ownedTokens) == 5

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [5])
    assert pos[0] == XYPool
    assert pos[4] == 45220
    assert pos[5] == 46130
    second_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [6])
    assert second_pos[0] == XYPool
    assert second_pos[4] ==41220
    assert second_pos[5] ==42130
    third_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [7])
    assert third_pos[0] == XYPool
    assert third_pos[4] == 47220
    assert third_pos[5] == 48130
    fourth_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [8])
    assert fourth_pos[0] == XYPool
    assert fourth_pos[4] == 44520
    assert fourth_pos[5] == 48130
    fifth_pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [9])
    assert fifth_pos[0] == XYPool
    assert fifth_pos[4] == 40320
    assert fifth_pos[5] == 41230

def remLiq(connector, ABPool, NFTContract, minter, tokenID, liquidity):

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])

    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    execute_functions(connector, 
                        minter,
                        NFTContract, NFTContract.address,
                        "removeLiquidity",
                        [[tokenID, liquidity]])
    # chain.sleep(30)
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])
    slot_zero = call_functions(connector, 
                        deployer,
                        XYPool, XYPool.address,
                        "slot0",
                        [])
    currentPrice = (slot_zero[0]/(2**96))**2
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

def addLiq(connector, deployer, Atoken, Btoken, NFTContract, amountA, amountB, minter, tokenID):
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])

    liquidity =  pos[1]
    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    execute_functions(connector, 
                        minter,
                        Atoken, Atoken.address,
                        "approve",
                        [NFTContract, amountA])
    execute_functions(connector, 
                        minter,
                        Btoken, Btoken.address,
                        "approve",
                        [NFTContract, amountB])

    execute_functions(connector, 
                        minter,
                        NFTContract, NFTContract.address,
                        "addLiquidity",
                        [tokenID, amountA, amountB, 0, 0])


    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])
    assert pos[1] > liquidity
    assert pos[2:] == (tokensOwed0, tokensOwed1, lowerTick, upperTick)

def collectLiq(connector, ABPool, NFTContract, minter, tokenID):

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])

    tokensOwed0 = pos[2]
    tokensOwed1 = pos[3]
    lowerTick = pos[4]
    upperTick = pos[5]

    execute_functions(connector, 
                        minter,
                        NFTContract, NFTContract.address,
                        "collect",
                        [tokenID])
    #chain.sleep(30)
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [tokenID])
    assert pos[0] == ABPool
    assert pos[1] == 0
    assert pos[2] == 0
    assert pos[3] == 0
    assert pos[4] == lowerTick
    assert pos[5] == upperTick




'''
TESTS
'''
def test_userToAllPos(connector,
                      deployer, Alice, Bob, Carol, 
                      Atoken, Btoken, ABPool,
                      Xtoken, Ytoken, XYPool,  
                      NFTContract, deployLibrary, swapManagerContract, 
                      init_setup_ABPool, init_setup_XYPool):
    #Accounts
    account= deployer

    #Mint some X and Y tokens to Alice
    execute_functions(connector, 
                        deployer,
                        Xtoken, Xtoken.address,
                        "mint",
                        [Alice, 100_000*10**18])
    execute_functions(connector, 
                        deployer,
                        Ytoken, Ytoken.address,
                        "mint",
                        [Alice, 100_000*10**18])

    #Alice: Set position in different pool
    set_pos(NFTContract, Alice, Xtoken, Ytoken, 500, 44220, 48130, 0.1*10**18, 10*10**18)

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 11
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Alice])
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (0,1,2,3,4,10)
    assert len(ownedTokens) == 6
    ownedTokensInfo = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "userToAllPositions",
                        [Alice])

    print('-----------------------\n Token pos info:')
    print(ownedTokensInfo)
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [10]) 
    assert pos[0] == XYPool
    assert pos[4] == 44220
    assert pos[5] == 48130

    #Alice: Delete position in AB pool
    #Remove all liquidity from Position 2
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [2]) 

    liquidity =  pos[1]
    remLiq(ABPool,NFTContract, Alice, 2, liquidity)

    #Collect tokens from Position 2
    collectLiq(ABPool, NFTContract, Alice, 2)

    #Burn token 2 position
    NFTContract.burn(2,{"from": Alice})

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 10
    print('Total token Supply:',tokens)
    print('-----------------------\n Token pos info:')
    print(ownedTokensInfo)
    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Alice])
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (0,1,3,4,10)
    assert len(ownedTokens) == 5
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [10]) 
    assert pos[0] == XYPool
    assert pos[4] == 44220
    assert pos[5] == 48130

    #Create new position after deleting the old one
    set_pos(NFTContract, Alice, Xtoken, Ytoken, 500, 43220, 49130, 0.1*10**18, 10*10**18)
    set_pos(NFTContract, Alice, Atoken, Btoken, 500, 84220, 86130, 1*10**18, 5000*10**18)

    tokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "totalSupply",
                        [])
    assert tokens == 12
    print('Total token Supply:',tokens)

    ownedTokens = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokensOfOwner",
                        [Alice])
    print('Tokens of Alice:',ownedTokens)
    assert ownedTokens == (0,1,3,4,10,11,12)
    assert len(ownedTokens) == 7
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [11]) 
    assert pos[0] == XYPool
    assert pos[4] == 43220
    assert pos[5] == 49130
    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [12]) 
    assert pos[0] == ABPool
    assert pos[4] == 84220
    assert pos[5] == 86130
    print('-----------------------\n Token pos info:')
    print(ownedTokensInfo)

    #After swap
    #Mint some A tokens for Bob to swap
    execute_functions(connector, 
                        deployer,
                        Atoken, Atoken.address,
                        "mint",
                        [Bob, 100_000*10**18])
    execute_functions(connector, 
                        Bob,
                        Atoken, Atoken.address,
                        "approve",
                        [swapManagerContract, 10*10**18])

    slippage = 0.03
    params = [Atoken, Btoken, 500, 0.1*10**18, int(int(ABPool.slot0({"from": account})[0])*math.sqrt(1-slippage))]
    swapResults =  execute_functions(connector, 
                        Bob,
                        swapManagerContract, swapManagerContract.address,
                        "swapSingle",
                        [params])

    pos = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "tokenIDtoPosition",
                        [12]) 

    liquidity =  0
    remLiq(ABPool,NFTContract, Alice, 12, liquidity)


    ownedTokensInfo = call_functions(connector, 
                        deployer,
                        NFTContract, NFTContract.address,
                        "userToAllPositions",
                        [Alice])

    print('-----------------------\n Token pos info:')
    print(ownedTokensInfo)