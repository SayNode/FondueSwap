// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.14;

import "./ABDKMath64x64.sol";
import "../lib/FixedPoint96.sol";
import "../interfaces/IUniswapV3Manager.sol";
import "../lib/TickMath.sol";

library Utils {
    function sqrtP(uint256 price) internal pure returns (uint160) {
        return
            uint160(
                int160(
                    ABDKMath64x64.sqrt(int128(int256(price << 64))) <<
                        (FixedPoint96.RESOLUTION - 64)
                )
            );
    }

    function mintParams(
        address tokenA,
        address tokenB,
        uint160 lowerSqrtP,
        uint160 upperSqrtP,
        uint256 amount0,
        uint256 amount1,
        uint24 fee
    ) internal pure returns (IUniswapV3Manager.MintParams memory params) {
        params = IUniswapV3Manager.MintParams({
            tokenA: tokenA,
            tokenB: tokenB,
            fee: fee,
            lowerTick: sqrtPToNearestTick(lowerSqrtP, 60),
            upperTick: sqrtPToNearestTick(upperSqrtP, 60),
            amount0Desired: amount0,
            amount1Desired: amount1,
            amount0Min: 0,
            amount1Min: 0
        });
    }

    function sqrtPToNearestTick(uint160 sqrtP_, uint24 tickSpacing)
        internal
        pure
        returns (int24 tick_)
    {
        tick_ = TickMath.getTickAtSqrtRatio(sqrtP_);
        tick_ = nearestUsableTick(tick_, tickSpacing);
    }

    function nearestUsableTick(int24 tick_, uint24 tickSpacing)
        internal
        pure
        returns (int24 result)
    {
        result =
            int24(divRound(int128(tick_), int128(int24(tickSpacing)))) *
            int24(tickSpacing);

        if (result < TickMath.MIN_TICK) {
            result += int24(tickSpacing);
        } else if (result > TickMath.MAX_TICK) {
            result -= int24(tickSpacing);
        }
    }

    function divRound(int128 x, int128 y)
        internal
        pure
        returns (int128 result)
    {
        int128 quot = ABDKMath64x64.div(x, y);
        result = quot >> 64;

        // Check if remainder is greater than 0.5
        if (quot % 2**64 >= 0x8000000000000000) {
            result += 1;
        }
    }
}
