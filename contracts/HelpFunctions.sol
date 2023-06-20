// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.14;

import "./interfaces/IUniswapV3Pool.sol";

import "./lib/PoolAddress.sol";

library HelpFunctions {
    error WrongToken();
    error PositionNotCleared();
    error NotAuthorized();
    error SlippageCheckFailed(uint256 amount0, uint256 amount1);
    error TooLittleReceived(uint256 amountOut);

    struct MintParams {
        address recipient;
        address tokenA;
        address tokenB;
        uint24 fee;
        int24 lowerTick;
        int24 upperTick;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
    }

    struct AddLiquidityInternalParams {
        IUniswapV3Pool pool;
        int24 lowerTick;
        int24 upperTick;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
    }

    struct TokenPosition {
        address pool;
        int24 lowerTick;
        int24 upperTick;
    }

    function _getPool(
        address factory,
        address token0,
        address token1,
        uint24 fee
    ) public pure returns (IUniswapV3Pool pool) {
        (token0, token1) = token0 < token1
            ? (token0, token1)
            : (token1, token0);
        pool = IUniswapV3Pool(
            PoolAddress.computeAddress(factory, token0, token1, fee)
        );
    }

    /*
        Returns position ID within a pool
    */
    function _poolPositionKey(
        TokenPosition memory position
    ) internal view returns (bytes32 key) {
        key = keccak256(
            abi.encodePacked(
                address(this),
                position.lowerTick,
                position.upperTick
            )
        );
    }

    /*
        Returns position ID within the NFT manager
    */
    function _positionKey(
        TokenPosition memory position
    ) internal pure returns (bytes32 key) {
        key = keccak256(
            abi.encodePacked(
                address(position.pool),
                position.lowerTick,
                position.upperTick
            )
        );
    }
}
