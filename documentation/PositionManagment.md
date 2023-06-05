# Contract Properties

## Variables to interact with:

- **totalSupply**[uint256, public]: total number of tokens that currently exist (minted and not burned)
- **nextTokenId**[uint256, private]: simply keeps track of the tokenId number that will be used for the next token minted

- **factory**[address, public, immutable]: address of the pool factory contract

- **positions**[mapping(uint256 => TokenPosition), public]: feed it a tokenId number and it will give you
  the pool, lowerTick and upperTick for the position
  represent by that token

- **userOwnedPositions**[mapping(address => uint256[]), public]: feed it an address and it will return all the tokenIds of the liquidity position NFTs the user has

- **burnedIds**[mapping(uint256 => bool), public]: keeps track if a tokenId has been burned

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
- _Function_: receives an array with parameters,
  and collects the tokens relative to a cleared position.
  Can only be called after the user has removed all liquidity
  from the position (removeLiquidity)
- _Receives_: receives an array with: - tokenId of the position - Amount of token X to be collected - Amount of token Y to be collected
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
- _Receives_: receives an array with: - tokenId - liquidity amount we wish to remove
- _Returns_:
  - new amount of token X in the position
  - new amount of token Y in the position

## Frontend operations:

- If the frontend wants to show the user all of his positions and their info it should:
  1. Call the tokensOfOwner function with the user address. This will return all the
     tokenIds owned by the user;
  2. Call tokenIDtoPosition using the intended tokenID to get that positions info
- If user wants to delete a position and get his tokens back:
  1. Call removeLiquidity
  2. Call collect
  3. Call burn

## Questions:

- Vtho produced by VET in pools. Is the contract the owner? Can the contract pay for txs?
- Can we use the Vechain stablecoin as an on-ramp?
- Multiple swaps at one time using multi-clause calls?
- Slippage prediction?

# Tests

## Test_SetPos

### Normal Functioning

- mint
- tokensOfOwner
- totalSupply
- tokenIDtoPosition

## Test_updatePos

### Normal Functioning

- addLiquidity
- removeLiquidity
- collect
- burn

### Errors

- NotAuthorized (trying to burn or collect a position not owned)
- PositionNotCleared (trying to burn or collect a position that still has liquidity)
