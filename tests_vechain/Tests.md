# Tests

The testing was made in the Vechain Remix. The idea is to see if every function works in Vechain in the same way it works in the Brownie eth fork, validating our testing on the later for the Vechain chain.

## Contracts

- Token A: 0x854aa996D5575bf7606c616b5a087CC2F0b1FEd4
- Token B: 0x92FfFbb6C65541E9679352B7028698725C26304D
- PoolFactory: 0x87006d97906c0787E8ad9394f47fb61887b80e28
- AB Pool: 0xaA856c7083992e350996bA591fBc3E021a084311
- NFT: 0x7c750B8ec959efc937493Ca573a9E29a2b75837E
- SwapManager: 0x2e0B13D839b3E468AB86bDd4A1171b9269d299a4

## Functions

- PoolCreation: 0x0ec675cf190d920006e173cd3d8a908d6d4659ddeb0ca938de2464828805dca5
- Pool Initialization: 0x48e67075a25ec9eb05565965d7bd6b83a8cd5928ae38e727ebba6231a31fb4f3
- Mint position 0 (in price range): 0x7ad03410354bd0f3e34090ac66847740ce81ff2bd4da000e7fed57ad4af87345
- Mint position 1 (bellow price range): 0xdfd80f4aaf4f171d8c28f421e757850dea5ed10edff7e096f7471654d66a5a49
- Mint position 2 (above price range): 0x149f7c95b4a74f08ff77ac69ee648484185d255db42a927b27ba340fdb1184db
- Mint position 3 (in price range): 0xb758d40435e2e8e75f7a9b5cb163aa7c2b75525ca1ed50ecffbbf57de9283485
- Mint position 4 (in price range): 0x944c94a6dcaf549ec4ea5e342c80c645003aca085f972985323f74b2cf17ce4b
- Add liquidity to position 0: 0x2967b5e4a38f4e12fce1cfbc4f6f6235348fae4c8b579e58e0ca8d09541d60de (verified with the tokenIDtoPosition)
- Remove Liquidity from position 2: 0x2b1213f0879621c1c9389ab399c65c19ec591bc231554287ca89f8d11a84a5d4 (verified with the tokenIDtoPosition)
- Swap:
- Collect:
- Burn:
