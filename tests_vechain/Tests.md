# Setup:

1. Deploy Tokens

   - "TokenA","TA",18
   - "TokenB","TB",18

2. Fund the wallet

   - 0x4E797d50aE049F047C425dA32b64305b0ebcf78a
   - 100000000000000000000000

3. Deploy PoolFactory
4. Create a pool with the 2 tokens and a fee

   - TokenA_address, TokenB_address, 500

5. Initialize the pool the P=5000
6. Deploy NFT
   - Factory_address
7. Deploy SwapManager
   - Factory_address

# Tests

The testing was made in the [Vechain Energy IDE](https://ide.vechain.energy/), which uses the Vechain testnet. The idea is to see if every function works in Vechain in the same way it works in the Brownie eth fork, validating our testing on the later for the Vechain chain.

The parameters used for each step described in [Functions](#functions-tested) can be checked in the Params.md in this same folder.

## Contracts

- Token A: 0x854aa996D5575bf7606c616b5a087CC2F0b1FEd4
- Token B: 0x92FfFbb6C65541E9679352B7028698725C26304D
- PoolFactory: 0x87006d97906c0787E8ad9394f47fb61887b80e28
- AB Pool: 0xaA856c7083992e350996bA591fBc3E021a084311
- NFT: 0x7c750B8ec959efc937493Ca573a9E29a2b75837E
- SwapManager: 0x2e0B13D839b3E468AB86bDd4A1171b9269d299a4

## Functions Tested

- PoolCreation: 0x0ec675cf190d920006e173cd3d8a908d6d4659ddeb0ca938de2464828805dca5
- Pool Initialization: 0x48e67075a25ec9eb05565965d7bd6b83a8cd5928ae38e727ebba6231a31fb4f3
- Mint position 0 (in price range): 0x7ad03410354bd0f3e34090ac66847740ce81ff2bd4da000e7fed57ad4af87345
- Mint position 1 (bellow price range): 0xdfd80f4aaf4f171d8c28f421e757850dea5ed10edff7e096f7471654d66a5a49
- Mint position 2 (above price range): 0x149f7c95b4a74f08ff77ac69ee648484185d255db42a927b27ba340fdb1184db
- Mint position 3 (in price range): 0xb758d40435e2e8e75f7a9b5cb163aa7c2b75525ca1ed50ecffbbf57de9283485
- Mint position 4 (in price range): 0x944c94a6dcaf549ec4ea5e342c80c645003aca085f972985323f74b2cf17ce4b
- Add liquidity to position 0: 0x2967b5e4a38f4e12fce1cfbc4f6f6235348fae4c8b579e58e0ca8d09541d60de (verified with the tokenIDtoPosition)
- Remove Liquidity from position 2: 0x2b1213f0879621c1c9389ab399c65c19ec591bc231554287ca89f8d11a84a5d4 (verified with the tokenIDtoPosition)
- Swap: 0x5de4d3e6ac31b26c31742d342c42193115477b889021a1786417998a660b4bb3
- See that position 0, 3 and 4 are owed fees since these are the ones in the range where the swap occurred using _getFees_
- Get the fees from position 3: 0x0261603686799488b8ae47cec0b1d7abaafab11227eb854666750406b7aa48f7
- Burn position 2:
  - Remove Liq: 0x290818d6ba5989e95ada87d06da5c4f9c2b3d9ff3461728ce89aa4767f72d806
  - Collect: 0xbe5567a70ca90e0ac505f49679d656bdfe222717436332b026ce1bfc03e8fe3b
  - Burn: 0x10adebc22ca6f3c913510e7b52eb61b26350d7699c4956a7606bf22ae1b4147d
  - Verified with _tokensOfOwner_, _tokenIDtoPosition_ and _totalSupply_
