import pytest

from brownie import (accounts, 
                    Contract, 
                    MockToken, 
                    UniswapV3Factory, UniswapV3Pool, 
                    UniswapV3ManagerMint, UniswapV3ManagerSwaps)

def main():
    pass
def setUp():
    # fetch the account
    account = accounts[0]

    # deploy contract
    Atoken = MockToken.deploy("TokenA","TA",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Atoken}")

    # deploy contract
    Btoken = MockToken.deploy("TokenB","TB",18,{"from":account})
    # print contract address
    print(f"Token contract deployed at {Btoken}")

    # deploy Staking contract
    factoryContract = UniswapV3Factory.deploy({"from":account})
    # print contract address
    print(f"Factory contract deployed at {factoryContract}")

    # deploy Staking contract
    mintManager = UniswapV3ManagerMint.deploy(factoryContract, {"from":account})
    # print contract address
    print(f"Mint manager contract deployed at {mintManager}")

    # deploy Staking contract
    swapManager = UniswapV3ManagerSwaps.deploy(factoryContract, {"from":account})
    # print contract address
    print(f"Swap manager contract deployed at { swapManager}")

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

    assert ABPool.slot0({"from": account})[0] != (0)

    #Fund the users
    Alice = accounts[1]
    Atoken.mint(Alice, 100000*10**18,{"from": account})
    Btoken.mint(Alice, 1000000*10**18,{"from": account})

    #Set pos
    Atoken.approve(mintManager, 100*10**18, {"from": Alice})
    Btoken.approve(mintManager, 500000*10**18, {"from": Alice})

    mintManager.mint([Atoken, Btoken, 500, 84220, 86130, 100*10**18, 500000*10**18, 0, 0], {"from": Alice} )

    pos = mintManager.getPosition([Atoken, Btoken, 500, Alice, 84220, 86130], {"from": Alice})
    print('Position:',pos)
    assert pos[0]!=0

    #Fund Bob
    Bob = accounts[2]
    Atoken.mint(Bob, 100*10**18,{"from": account})

    #Bob wants to swap 1 A token so it approves 1
    Atoken.approve(swapManager, 1*10**18, {"from": Bob})
    print('\n-----------Balances before swap:-----------')
    print('Atoken=',int(Atoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('Btoken=',int(Btoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('--------------------------------------------\n')

    params = [Atoken, Btoken, 500, 1*10**18, int(int(ABPool.slot0({"from": account})[0])*0.9)]
    tx = swapManager.swapSingle(params, {"from": Bob} )

    print('\n-----------Balances after swap:-----------')
    print('Atoken=',int(Atoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('Btoken=',int(Btoken.balanceOf(Bob, {"from": Bob}))/10**18)
    print('--------------------------------------------\n')
setUp()