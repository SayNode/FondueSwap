// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.14;

import "./PoolFactory.sol";
import "./HelpFunctions.sol";

import "../interfaces/IERC20.sol";
import "../interfaces/IUniswapV3Pool.sol";
import "../interfaces/IUniswapV3Manager.sol";

import "./lib/Path.sol";
import "./lib/PoolAddress.sol";
import "./lib/TickMath.sol";

contract SwapManager is IUniswapV3Manager {
    using Path for bytes;

    event Log(string message, uint24 data);

    address public immutable factory;

    PoolFactory fact;

    /*
    Constructor
    */
    constructor(address factory_) {
        factory = factory_;
        fact = PoolFactory(factory);
    }

    /*
    Public 
    */
    /// @notice makes a single pool swap
    /// @param params: an array with the following parameters:
    ///             tokenIn: the token we want to sell to the pool
    ///             tokenOut: the token we want to buy from the pool
    ///             fee: the fee of the pool in which we will swap
    ///             amountIn: amount of the token we want to sell
    ///             sqrtPriceLimitX96: how much we are willing to allow for price slippage SQRTP*sqrt(slippage)
    /// @dev cannot be used unless the pool exists
    function swapSingle(
        SwapSingleParams calldata params
    ) public returns (uint256 amountOut) {
        amountOut = _swap(
            params.amountIn,
            msg.sender,
            params.sqrtPriceLimitX96,
            SwapCallbackData({
                path: abi.encodePacked(
                    params.tokenIn,
                    params.fee,
                    params.tokenOut
                ),
                payer: msg.sender
            })
        );
    }

    /// @notice makes multiple-pool swaps
    /// @param params: an array with the following parameters:
    ///             path: the hex code of the pool paths that are part of the multi-swap
    ///             recipient: who will receive the tokens
    ///             amountIn: the amount of tokens we want to sell
    ///             minAmountOut: the minimum amount of tokens we are willing to receive
    /// @dev should only be used if there is no direct trade pool
    function swapMulti(
        SwapParams memory params
    ) public returns (uint256 amountOut) {
        address payer = msg.sender;
        bool hasMultiplePools;

        while (true) {
            hasMultiplePools = params.path.hasMultiplePools();

            params.amountIn = _swap(
                params.amountIn,
                hasMultiplePools ? address(this) : params.recipient,
                0,
                SwapCallbackData({
                    path: params.path.getFirstPool(),
                    payer: payer
                })
            );

            if (hasMultiplePools) {
                payer = address(this);
                params.path = params.path.skipToken();
            } else {
                amountOut = params.amountIn;
                break;
            }
        }

        if (amountOut < params.minAmountOut)
            revert HelpFunctions.TooLittleReceived(amountOut);
    }

    function uniswapV3SwapCallback(
        int256 amount0,
        int256 amount1,
        bytes calldata data_
    ) public {
        SwapCallbackData memory data = abi.decode(data_, (SwapCallbackData));
        (address tokenIn, address tokenOut, ) = data.path.decodeFirstPool();

        bool zeroForOne = tokenIn < tokenOut;

        int256 amount = zeroForOne ? amount0 : amount1;

        if (data.payer == address(this)) {
            IERC20(tokenIn).transfer(msg.sender, uint256(amount));
        } else {
            IERC20(tokenIn).transferFrom(
                data.payer,
                msg.sender,
                uint256(amount)
            );
        }
    }

    /*
    Public - View
     */
    function getPosition(
        GetPositionParams calldata params
    )
        public
        view
        returns (
            uint128 liquidity,
            uint256 feeGrowthInside0LastX128,
            uint256 feeGrowthInside1LastX128,
            uint128 tokensOwed0,
            uint128 tokensOwed1
        )
    {
        IUniswapV3Pool pool = HelpFunctions._getPool(
            factory,
            params.tokenA,
            params.tokenB,
            params.fee
        );

        (
            liquidity,
            feeGrowthInside0LastX128,
            feeGrowthInside1LastX128,
            tokensOwed0,
            tokensOwed1
        ) = pool.positions(
            keccak256(
                abi.encodePacked(
                    params.owner,
                    params.lowerTick,
                    params.upperTick
                )
            )
        );
    }

    /*
    Internal
    */
    /// @notice helper function for both single and multi swaps
    /// @param amountIn: amount of token to sell
    /// @param recipient: who will receive the bought tokens
    /// @param sqrtPriceLimitX96: maximum price deviation
    function _swap(
        uint256 amountIn,
        address recipient,
        uint160 sqrtPriceLimitX96,
        SwapCallbackData memory data
    ) internal returns (uint256 amountOut) {
        (address tokenIn, address tokenOut, uint24 fee) = data
            .path
            .decodeFirstPool();

        bool zeroForOne = tokenIn < tokenOut;

        (int256 amount0, int256 amount1) = HelpFunctions
            ._getPool(factory, tokenIn, tokenOut, fee)
            .swap(
                recipient,
                zeroForOne,
                amountIn,
                sqrtPriceLimitX96 == 0
                    ? (
                        zeroForOne
                            ? TickMath.MIN_SQRT_RATIO + 1
                            : TickMath.MAX_SQRT_RATIO - 1
                    )
                    : sqrtPriceLimitX96,
                abi.encode(data)
            );

        amountOut = uint256(-(zeroForOne ? amount1 : amount0));
    }
}
