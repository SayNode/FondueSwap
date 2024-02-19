// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.14;

import "./HelpFunctions.sol";
import "./PoolFactory.sol";

import "../interface_contracts/IUniswapV3Pool.sol";

import "./lib/Math.sol";
import "./lib/Path.sol";
import "./lib/PoolAddress.sol";
import "./lib/TickMath.sol";
import "./lib/LiquidityMath.sol";

contract Quoter {
    using Path for bytes;

    address public immutable factory;
    PoolFactory poolfactory;

    constructor(address factory_) {
        factory = factory_;
        poolfactory = PoolFactory(factory);
    }

    /*
    External
     */
    function uniswapV3SwapCallback(
        int256 amount0Delta,
        int256 amount1Delta,
        bytes memory data
    ) external view {
        address pool = abi.decode(data, (address));
        uint256 amountOut = amount0Delta > 0
            ? uint256(-amount1Delta)
            : uint256(-amount0Delta);
        (uint160 sqrtPriceX96After, int24 tickAfter, , , ) = IUniswapV3Pool(
            pool
        ).slot0();
        assembly {
            let ptr := mload(0x40)
            mstore(ptr, amountOut)
            mstore(add(ptr, 0x20), sqrtPriceX96After)
            mstore(add(ptr, 0x40), tickAfter)
            revert(ptr, 96)
        }
    }

    /*
    Public
     */
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
            ) = quoteSingle(tokenIn, tokenOut, fee,  amountIn, 0
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
        address tokenIn,
        address tokenOut,
        uint24 fee,
        uint256 amountIn,
        uint160 sqrtPriceLimitX96
    )
        public
        returns (uint256 amountOut, uint160 sqrtPriceX96After, int24 tickAfter)
    {
        IUniswapV3Pool pool = IUniswapV3Pool(poolfactory.pools(
            tokenIn,
            tokenOut,
            fee
        )); 
 
        bool zeroForOne = tokenIn < tokenOut;

        try
            pool.swap(
                address(this),
                zeroForOne,
                amountIn,
                sqrtPriceLimitX96 == 0
                    ? (
                        zeroForOne
                            ? TickMath.MIN_SQRT_RATIO + 1
                            : TickMath.MAX_SQRT_RATIO - 1
                    )
                    : sqrtPriceLimitX96,
                abi.encode(address(pool))
            )
        {} catch (bytes memory reason) {
            bytes32 hashedRes = keccak256(reason);
            if (keccak256(abi.encodeWithSignature("InvalidPriceLimit()")) == hashedRes) {
                revert('InvalidPriceLimit');
            }else if (keccak256(abi.encodeWithSignature("NotEnoughLiquidity()")) == hashedRes){
                revert('NotEnoughLiquidity');
            }
            return abi.decode(reason, (uint256, uint160, int24));
        } 
    }

    /*
    Public - View
     */
    function quoteLiqInputToken0(
                address tokenIn,
        address tokenOut,
        uint24 fee,
        int24 lowerTick,
        int24 upperTick,
        uint256 amountInDesired
    ) public view returns (uint256 amount1) {
        IUniswapV3Pool pool = IUniswapV3Pool(poolfactory.pools(
            tokenIn,
            tokenOut,
            fee
        )); 
        (uint160 sqrtPriceX96, int24 tick, , , ) = pool.slot0();

        if (tick < upperTick && tick > lowerTick) {
            amount1 = Math.mulDivRoundingUp(
                uint256(sqrtPriceX96),
                uint256(amountInDesired),
                uint256(2 ** 96)
            );

            uint128 liquidity = _getLiquidity(
                lowerTick,
                upperTick,
                sqrtPriceX96,
                amountInDesired,
                amount1 ** 2
            );

            amount1 = Math.calcAmount1Delta(
                TickMath.getSqrtRatioAtTick(lowerTick),
                sqrtPriceX96,
                liquidity,
                false
            );
        }
    }

    function quoteLiqInputToken1(
                address tokenIn,
        address tokenOut,
        uint24 fee,
        int24 lowerTick,
        int24 upperTick,
        uint256 amountInDesired
    ) public view returns (uint256 amount0) {
        IUniswapV3Pool pool = IUniswapV3Pool(poolfactory.pools(
            tokenIn,
            tokenOut,
            fee
        )); 

        (uint160 sqrtPriceX96, int24 tick, , , ) = pool.slot0();

        if (tick < upperTick && tick > lowerTick) {
            amount0 = Math.divRoundingUp(
                amountInDesired,
                Math.divRoundingUp(uint256(sqrtPriceX96), uint256(2 ** 96))
            );

            uint128 liquidity = _getLiquidity(
                lowerTick,
                upperTick,
                sqrtPriceX96,
                amount0 ** 2,
                amountInDesired
            );

            amount0 = Math.calcAmount0Delta(
                sqrtPriceX96,
                TickMath.getSqrtRatioAtTick(upperTick),
                liquidity,
                false
            );
        }
    }

    /*
    Internal - Pure
     */
    function _getLiquidity(
        int24 lowerTick,
        int24 upperTick,
        uint160 sqrtPriceX96,
        uint256 amountInDesired,
        uint256 amountOutDesired
    ) internal pure returns (uint128 liquidity) {
        liquidity = LiquidityMath.getLiquidityForAmounts(
            sqrtPriceX96,
            TickMath.getSqrtRatioAtTick(lowerTick),
            TickMath.getSqrtRatioAtTick(upperTick),
            amountInDesired,
            amountOutDesired
        );
    }
}
