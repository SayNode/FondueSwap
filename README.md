# Modifications

## UniswapV3Pool

- Pool used to be initialized with the sqrtPriceX96 (uint160) but I made it so it is initialized by the normal price. Than I added a function that calculates the sqrtPrice (Utils.sol->sqrtP) inside the initialize. This is to help the goal of making all calculations inside the contracts (avoid math problems from calcs in different languages/interpreters)

# TO DO

## UniswapV3ManagerSwaps

- Make that the sqrtPriceLimitX96 is calculated within the contract with acertain eprcentage of price slippage

## NFT

- In mint, do it so it receives the price and not the tick. We can do this using the function getTickAtSqrtRatio in the TickMath library

## IMPORTANT - TO DO

To reduce contract size, create a separate contract and interface that will have the

- struct AddLiquidityInternalParams
- function \_addLiquidity(
  AddLiquidityInternalParams memory params
  ) internal returns (uint128 liquidity, uint256 amount0, uint256 amount1)

- function \_getPool(
  address token0,
  address token1,
  uint24 fee
  ) internal view returns (IUniswapV3Pool pool)

  /_
  Returns position ID within a pool
  _/

- function \_poolPositionKey(
  TokenPosition memory position
  ) internal view returns (bytes32 key)

  /_
  Returns position ID within the NFT manager
  _/

- function \_positionKey(
  TokenPosition memory position
  ) internal pure returns (bytes32 key)

This way we can remove them from NFT and from UniswapV3NFTManager

# DONE

Split NFT manager into 2 (NFTManager and NFT) and changed it so they both do not exceed size and can access
position mappings by replacing

TokenPosition memory tokenPosition = nft.positions[params.tokenId];

with

        (address _pool, int24 _lowerTick, int24 _upperTick) = nft
            .tokenIDtoPosition(params.tokenId);

        TokenPosition memory tokenPosition = TokenPosition(
            _pool,
            _lowerTick,
            _upperTick
        );

- Created the swap and mint frontends (beta)
- Reduce contract size
- UniswapV3ManagerMint eliminated
