# Contract Properties

## Functions to interact with:

### swapSingle

- _Use_: Contract alteration
- _Function_: receives an array with parameters and preforms a swap in an existing pool
- _Receives_: receives an array with:
  - Token X address
  - Token Y address
  - pool fee
  - Amount of token X
  - Min amount of token Y the swapper is willing to receive
- _Returns_: the amount of token Y received

### swap

- _Use_: Contract alteration
- _Function_: receives an array with parameters and preforms a swap across multiple pools, to compensate for pools that do not exist
- _Receives_: receives an array with:
  - swap path: the concatenated hex of the various pools involved in the swap (see _getMultiPoolPath.py_)
  - minter address
  - Amount of token X
  - Min amount of token Y the swapper is willing to receive
- _Returns_: the amount of token Y received

## Frontend operations:

- If the frontend wants to find the pool path for the multi pool swaps:
  1. Created pools should be save in a back end as nodes in a graph
  2. We should call the backend with 2 tokens and get the smallest path between them

# Tests

## Test_SingleSwap

### Normal Functioning

- swapSingle

### Errors

- NotEnoughLiquidity (trying to swap through a single pool)

## Test_MultiSwap

### Normal Functioning

- multiSwap

### Errors

- NotEnoughLiquidity (trying to swap through multiple pools)
