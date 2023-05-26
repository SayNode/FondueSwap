// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.14;

import "./interfaces/IUniswapV3Pool.sol";
import "./lib/PoolAddress.sol";

library HelpFunctions {
    error WrongToken();
    error PositionNotCleared();
    error NotAuthorized();
    error SlippageCheckFailed(uint256 amount0, uint256 amount1);

    // function _tokenURI(
    //     address receivedPool,
    //     int24 lowerTick,
    //     int24 upperTick
    // ) public view returns (string memory) {
    //     if (receivedPool == address(0x00)) revert WrongToken();

    //     IUniswapV3Pool pool = IUniswapV3Pool(receivedPool);

    //     return
    //         NFTRenderer.render(
    //             NFTRenderer.RenderParams({
    //                 pool: receivedPool,
    //                 owner: address(this),
    //                 lowerTick: lowerTick,
    //                 upperTick: upperTick,
    //                 fee: pool.fee()
    //             })
    //         );
    // }

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

    // function helpMint(
    //     address factory,
    //     MintParams memory params
    // ) public view returns (IUniswapV3Pool) {
    //     IUniswapV3Pool pool = _getPool(
    //         factory,
    //         params.tokenA,
    //         params.tokenB,
    //         params.fee
    //     );

    //     return (pool);
    // }

    function helpBurn(TokenPosition memory tokenPosition) public view {
        if (tokenPosition.pool == address(0x00)) revert WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);
        (uint128 liquidity, , , uint128 tokensOwed0, uint128 tokensOwed1) = pool
            .positions(_poolPositionKey(tokenPosition));

        if (liquidity > 0 || tokensOwed0 > 0 || tokensOwed1 > 0)
            revert PositionNotCleared();
    }

    struct TokenPosition {
        address pool;
        int24 lowerTick;
        int24 upperTick;
    }
    ////////////////////////////////////////////////////////////////////////////
    //
    // INTERNAL
    //
    ////////////////////////////////////////////////////////////////////////////
    struct AddLiquidityInternalParams {
        IUniswapV3Pool pool;
        int24 lowerTick;
        int24 upperTick;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
    }

    function _addLiquidity(
        AddLiquidityInternalParams memory params
    ) internal returns (uint128 liquidity, uint256 amount0, uint256 amount1) {
        (uint160 sqrtPriceX96, , , , ) = params.pool.slot0();

        liquidity = LiquidityMath.getLiquidityForAmounts(
            sqrtPriceX96,
            TickMath.getSqrtRatioAtTick(params.lowerTick),
            TickMath.getSqrtRatioAtTick(params.upperTick),
            params.amount0Desired,
            params.amount1Desired
        );

        (amount0, amount1) = params.pool.mint(
            address(this),
            params.lowerTick,
            params.upperTick,
            liquidity,
            abi.encode(
                IUniswapV3Pool.CallbackData({
                    token0: params.pool.token0(),
                    token1: params.pool.token1(),
                    payer: msg.sender
                })
            )
        );

        if (amount0 < params.amount0Min || amount1 < params.amount1Min)
            revert SlippageCheckFailed(amount0, amount1);
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
