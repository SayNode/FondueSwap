# Contract Properties

## Functions to interact with:

### quoteSingle

- _Use_: Frontend
- _Function_: receives an array with parameters and preforms tells us the outcome of a swap
- _Receives_: receives an array with:
  - Token X address
  - Token Y address
  - pool fee
  - Amount of token X
  - Max price variation we can accept
- _Returns_:
  - amountOut: the amount of Y the user will receive after the swap is done
  - sqrtPriceX96After: the new pool price after the swap is done
  - tickAfter: the new pool current tick after the swap is done

### quoteMulti

- _Use_: Frontend
- _Function_: receives an array with parameters and preforms tells us the outcome of a swap
- _Receives_:
  - swap path: the concatenated hex of the various pools involved in the swap (see _getMultiPoolPath.py_)
  - Token X in amount
- _Returns_:
  - amountOut: the amount of the bought token the user will receive after the swap is done
  - sqrtPriceX96After: the new pool prices after all the swaps are done
  - tickAfter: the new pools current ticks after all the swaps are done

## Frontend operations:

- If the frontend wants to find the pool path for the multi pool swaps:
  1. Created pools should be save in a back end as nodes in a graph
  2. We should call the backend with 2 tokens and get the smallest path between them
- If the frontend wants to show a user a possible swap outcome:
  1. Checks if a pool exists for the trade, otherwise it will get the pool path
  2. Depending on 1 it either calls _quoteSingle_ or _quoteMulti_

# Tests

## Test_Quoter

### Normal Functioning

- quoteSingle
- quoteMulti
