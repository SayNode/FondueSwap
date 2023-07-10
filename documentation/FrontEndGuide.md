# NFT

## Functions to interact with:

### tokensOfOwner

- _Use_: Frontend
- _Function_: receives an address and returns all the token Ids owned by that address
- _Receives_: an address
- _Returns_: an array with all the tokenIds that address owns

### tokenIDtoPosition

- _Use_: Frontend
- _Function_: receives a tokenId and returns all the information regarding that tokens position
- _Receives_: a tokenId number
- _Returns_:
  - the pool the position belongs token
  - liquidity of the position
  - the tokens the user can withdraw+fees earned (both for token X and token Y)
  - lower tick
  - upper tick

### userToAllPositions

- _Use_: Frontend
- _Function_: receives an user address and returns all the information regarding all the token positions he has
- _Receives_: an user address
- _Returns_:
  - an array of the pool each position belongs to
  - an array of the liquidity of each position
  - an array of the tokens the user can withdraw
  - an array of the lower ticks
  - an array of the upper ticks

### userToAllPositionsFees

- _Use_: Frontend
- _Function_: receives an user address and returns all the fees regarding all the token positions he has
- _Receives_: an user address
- _Returns_:
  - an array of the token X fees each position is owed
  - an array of the token Y fees each position is owed

### mint

- _Use_: Contract alteration
- _Function_: receives an array with parameters, creates a position NFT and sets liquidity in the pool
- _Receives_: receives an array with:
  - minter address
  - Token X address
  - Token Y address
  - pool fee
  - lower tick
  - upper tick
  - Amount of token X
  - Amount of token Y
  - Min amount of token X (we will just put 0 here)
  - Min amount of token Y (we will just put 0 here)
- _Returns_: the tokenId of the liquidity position

### burn

- _Use_: Contract alteration
- _Function_: receives a tokenId and burns the corresponding NFT.
  Will fail if the user hasn't removed all liquidity
  from the position (removeLiquidity) and collected the
  corresponding tokens from this contract (collect).
  Useful for the user to clean his positions (he stops
  seeing this NFT every time he requests his positions)
- _Receives_: a tokenId
- _Returns_: nothing

### collect

- _Use_: Contract alteration
- _Function_: receives a tokenID,
  and collects the tokens relative to a cleared (or partially) position.
  Can only be called after the user has removed some liquidity
  from the position (removeLiquidity)
- _Receives_:
  - tokenId of the position
- _Returns_: the amounts of tokenX and token Y that were collected

### addLiquidity

- _Use_: Contract alteration
- _Function_: receives an array with parameters, and adds liquidity to an existing position.
  Does not mint any NFT.
- _Receives_: receives an array with:
  - tokenId
  - Amount of token X we want to add to the position
  - Amount of token Y we want to add to the position
  - Min amount of token X we want to add to the position(we will just put 0 here)
  - Min amount of token Y we want to add to the position (we will just put 0 here)
- _Returns_:
  - the new liquidity of the position
  - new amount of token X in the position
  - new amount of token Y in the position

### removeLiquidity

- _Use_: Contract alteration
- _Function_: receives an array with parameters, and removes a specified amount of liquidity
  from an existing position.
  Does not burn any NFT.
- _Receives_: receives an array with:
  - tokenId
  - liquidity amount we wish to remove => we can get the whole liquidity _tokenIdToPosition_ and then do %
- _Returns_:
  - new amount of token X in the position
  - new amount of token Y in the position

# SwapManager

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

### swapMulti

- _Use_: Contract alteration
- _Function_: receives an array with parameters and preforms a swap across multiple pools, to compensate for pools that do not exist
- _Receives_: receives an array with:
  - swap path: the concatenated hex of the various pools involved in the swap (see _getMultiPoolPath.py_)
  - minter address
  - Amount of token X
  - Min amount of token Y the swapper is willing to receive
- _Returns_: the amount of token Y received

## Quoter

## Functions to interact with:

### quoteLiqInputToken0

- _Use_: Frontend
- _Function_: receives an array with parameters and tells us how much of tokenY we will provide when adding liquidity/minting a position with a certain amount of Xtoken
- _Receives_: receives an array with:
  - Token X address
  - Token Y address
  - pool fee
  - Lower tick of position
  - Upper tick of position
- _Returns_:
  - amount1: the amount of token Y needed to add the amount of liquidity

### quoteLiqInputToken1

- _Use_: Frontend
- _Function_: receives an array with parameters and tells us how much of token X we will provide when adding liquidity/minting a position with a certain amount of token Y
- _Receives_: receives an array with:
  - Token Y address
  - Token X address
  - pool fee
  - Lower tick of position
  - Upper tick of position
- _Returns_:
  - amount0: the amount of token X needed to add the amount of liquidity
  -

### quoteSingle

- _Use_: Frontend
- _Function_: receives an array with parameters and tells us the outcome of a swap
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

# Instructions

## Pool Factory

- Create pool:
  1. Call _createPool_ (PoolFactory.sol) with the token addresses and the intended fee

## NFT

- User position info
  1. Call the _userToAllPositions_ (NFT.sol) function with the user address;
- User owed fees for all positions:
  1. Call the _userToAllPositionsFees_ (NFT.sol) function with the user address;
- User wants to delete a position and get his tokens back:
  1. Call _removeLiquidity_ (NFT.sol), and specify how much liquidity you want to remove
  2. Call _collect_ (NFT.sol)
  3. Call _burn_ (NFT.sol)
- To mint a new position:
  1. The user specifies either the amount of token X or token Y he wants to add;
  2. Depending if the user choose X or Y, call _quoteLiqInputToken0_ or _quoteLiqInputToken1_ (Quoter.sol), respectively, to get the other token amount;
  3. Call _mint_ (NFT.sol) with the previous two amounts
- To add liquidity:
  1. The user specifies either the amount of token X or token Y he wants to add;
  2. Depending if the user choose X or Y, call _quoteLiqInputToken0_ or _quoteLiqInputToken1_ (Quoter.sol), respectively, to get the other token amount;
  3. Call _addLiquidity_ (NFT.sol), and the user specifies percentage of slippage he his comfortable with;
- To remove only the earned fees:
  1. Call _removeLiquidity_ (NFT.sol) but use 0 as liquidity. This will update the user owned position and hence the fee amount. After that call _collect_ (NFT.sol)

## SwapManager

- Single pool swap:
  1. The user specifies the amount of token he wants to sell, and we call _quoteSingle_ (Quoter.sol);
  2. Use those values to call _swapSingle_ (SwapManager.sol)
- Multi pool swap:
  1. Find the necessary path and encoded (examples in scripts/poolPathCreator.py and tests/getMultiPoolPath.py, respectively);
  1. The user specifies the amount of token he wants to sell, and we call _quoteMulti_ (Quoter.sol);
  1. Use those values to call _swapMulti_ (SwapManager.sol)
