// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.14;

import "./HelpFunctions.sol";

import "./interfaces/IUniswapV3Pool.sol";

import "./lib/Math.sol";
import "./lib/Path.sol";
import "./lib/PoolAddress.sol";
import "./lib/TickMath.sol";
import "./lib/LiquidityMath.sol";

contract Quoter {
    using Path for bytes;

    struct QuoteSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        uint256 amountIn;
        uint160 sqrtPriceLimitX96;
    }

    struct LiqInputTokenParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        int24 lowerTick;
        int24 upperTick;
        uint256 amountInDesired;
    }

    address public immutable factory;

    constructor(address factory_) {
        factory = factory_;
    }

    function quoteLiqInputToken0(
        LiqInputTokenParams memory params
    ) external view returns (uint256 amount1) {
        uint128 liqY = LiquidityMath.getLiquidityForAmount0(
            TickMath.getSqrtRatioAtTick(params.lowerTick),
            TickMath.getSqrtRatioAtTick(params.upperTick),
            params.amountInDesired
        );

        IUniswapV3Pool pool = HelpFunctions._getPool(
            factory,
            params.tokenIn,
            params.tokenOut,
            params.fee
        );

        (uint160 sqrtPriceX96, int24 tick, , , ) = pool.slot0();

        if (tick < params.lowerTick) {
            amount1 = 0;
        } else if (tick < params.upperTick) {
            amount1 = Math.calcAmount1Delta(
                TickMath.getSqrtRatioAtTick(params.lowerTick),
                sqrtPriceX96,
                liqY,
                false
            );
        } else {
            amount1 = Math.calcAmount1Delta(
                TickMath.getSqrtRatioAtTick(params.lowerTick),
                TickMath.getSqrtRatioAtTick(params.upperTick),
                liqY,
                false
            );
        }
    }

    function quoteLiqInputToken1(
        LiqInputTokenParams memory params
    ) public view returns (uint256 amount0) {
        uint128 liqX = LiquidityMath.getLiquidityForAmount1(
            TickMath.getSqrtRatioAtTick(params.lowerTick),
            TickMath.getSqrtRatioAtTick(params.upperTick),
            params.amountInDesired
        );

        IUniswapV3Pool pool = HelpFunctions._getPool(
            factory,
            params.tokenIn,
            params.tokenOut,
            params.fee
        );

        (uint160 sqrtPriceX96, int24 tick, , , ) = pool.slot0();

        if (tick < params.lowerTick) {
            amount0 = Math.calcAmount0Delta(
                TickMath.getSqrtRatioAtTick(params.lowerTick),
                TickMath.getSqrtRatioAtTick(params.upperTick),
                liqX,
                true
            );
        } else if (tick < params.upperTick) {
            amount0 = Math.calcAmount0Delta(
                sqrtPriceX96,
                TickMath.getSqrtRatioAtTick(params.upperTick),
                liqX,
                true
            );
        }
    }

    function quoteMulti(
        bytes memory path,
        uint256 amountIn
    )
        public
        returns (
            uint256 amountOut,
            uint160[] memory sqrtPriceX96AfterList,
            int24[] memory tickAfterList
        )
    {
        sqrtPriceX96AfterList = new uint160[](path.numPools());
        tickAfterList = new int24[](path.numPools());

        uint256 i = 0;
        while (true) {
            (address tokenIn, address tokenOut, uint24 fee) = path
                .decodeFirstPool();

            (
                uint256 amountOut_,
                uint160 sqrtPriceX96After,
                int24 tickAfter
            ) = quoteSingle(
                    QuoteSingleParams({
                        tokenIn: tokenIn,
                        tokenOut: tokenOut,
                        fee: fee,
                        amountIn: amountIn,
                        sqrtPriceLimitX96: 0
                    })
                );

            sqrtPriceX96AfterList[i] = sqrtPriceX96After;
            tickAfterList[i] = tickAfter;
            amountIn = amountOut_;
            i++;

            if (path.hasMultiplePools()) {
                path = path.skipToken();
            } else {
                amountOut = amountIn;
                break;
            }
        }
    }

    function quoteSingle(
        QuoteSingleParams memory params
    )
        public
        returns (uint256 amountOut, uint160 sqrtPriceX96After, int24 tickAfter)
    {
        IUniswapV3Pool pool = HelpFunctions._getPool(
            factory,
            params.tokenIn,
            params.tokenOut,
            params.fee
        );

        bool zeroForOne = params.tokenIn < params.tokenOut;

        try
            pool.swap(
                address(this),
                zeroForOne,
                params.amountIn,
                params.sqrtPriceLimitX96 == 0
                    ? (
                        zeroForOne
                            ? TickMath.MIN_SQRT_RATIO + 1
                            : TickMath.MAX_SQRT_RATIO - 1
                    )
                    : params.sqrtPriceLimitX96,
                abi.encode(address(pool))
            )
        {} catch (bytes memory reason) {
            return abi.decode(reason, (uint256, uint160, int24));
        }
    }
}
