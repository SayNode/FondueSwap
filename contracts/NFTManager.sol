// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.14;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./HelpFunctions.sol";

import "./interfaces/INFT.sol";
import "./interfaces/IERC20.sol";
import "./interfaces/IUniswapV3Pool.sol";
import "./lib/LiquidityMath.sol";
import "./lib/NFTRenderer.sol";
import "./lib/PoolAddress.sol";
import "./lib/TickMath.sol";

contract NFTManager {
    error NotAuthorized();
    error NotEnoughLiquidity();
    error PositionNotCleared();
    error SlippageCheckFailed(uint256 amount0, uint256 amount1);
    error WrongToken();

    event AddLiquidity(
        uint256 indexed tokenId,
        uint128 liquidity,
        uint256 amount0,
        uint256 amount1
    );

    event RemoveLiquidity(
        uint256 indexed tokenId,
        uint128 liquidity,
        uint256 amount0,
        uint256 amount1
    );

    uint256 public totalSupply;

    address public immutable factory;
    INFT public immutable nft;

    modifier isApprovedOrOwner(uint256 tokenId) {
        address owner = nft.ownerOf(tokenId);
        if (
            msg.sender != owner &&
            !(nft.isApprovedForAll(owner, msg.sender)) &&
            nft.getApproved(tokenId) != msg.sender
        ) revert NotAuthorized();

        _;
    }

    constructor(address factoryAddress, address nftAddress) {
        factory = factoryAddress;
        nft = INFT(nftAddress);
    }

    struct AddLiquidityParams {
        uint256 tokenId;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
    }

    function addLiquidity(
        AddLiquidityParams calldata params
    ) public returns (uint128 liquidity, uint256 amount0, uint256 amount1) {
        (address _pool, int24 _lowerTick, int24 _upperTick) = nft
            .tokenIDtoPosition(params.tokenId);

        HelpFunctions.TokenPosition memory tokenPosition = HelpFunctions
            .TokenPosition(_pool, _lowerTick, _upperTick);

        if (tokenPosition.pool == address(0x00)) revert WrongToken();

        (liquidity, amount0, amount1) = HelpFunctions._addLiquidity(
            HelpFunctions.AddLiquidityInternalParams({
                pool: IUniswapV3Pool(tokenPosition.pool),
                lowerTick: tokenPosition.lowerTick,
                upperTick: tokenPosition.upperTick,
                amount0Desired: params.amount0Desired,
                amount1Desired: params.amount1Desired,
                amount0Min: params.amount0Min,
                amount1Min: params.amount1Min
            })
        );

        emit AddLiquidity(params.tokenId, liquidity, amount0, amount1);
    }

    struct RemoveLiquidityParams {
        uint256 tokenId;
        uint128 liquidity;
    }

    // TODO: add slippage check
    function removeLiquidity(
        RemoveLiquidityParams memory params
    )
        public
        isApprovedOrOwner(params.tokenId)
        returns (uint256 amount0, uint256 amount1)
    {
        (address _pool, int24 _lowerTick, int24 _upperTick) = nft
            .tokenIDtoPosition(params.tokenId);

        HelpFunctions.TokenPosition memory tokenPosition = HelpFunctions
            .TokenPosition(_pool, _lowerTick, _upperTick);

        if (tokenPosition.pool == address(0x00)) revert WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);

        (uint128 availableLiquidity, , , , ) = pool.positions(
            HelpFunctions._poolPositionKey(tokenPosition)
        );
        if (params.liquidity > availableLiquidity) revert NotEnoughLiquidity();

        (amount0, amount1) = pool.burn(
            tokenPosition.lowerTick,
            tokenPosition.upperTick,
            params.liquidity
        );

        emit RemoveLiquidity(
            params.tokenId,
            params.liquidity,
            amount0,
            amount1
        );
    }

    struct CollectParams {
        uint256 tokenId;
        uint128 amount0;
        uint128 amount1;
    }

    function collect(
        CollectParams memory params
    )
        public
        isApprovedOrOwner(params.tokenId)
        returns (uint128 amount0, uint128 amount1)
    {
        (address _pool, int24 _lowerTick, int24 _upperTick) = nft
            .tokenIDtoPosition(params.tokenId);

        HelpFunctions.TokenPosition memory tokenPosition = HelpFunctions
            .TokenPosition(_pool, _lowerTick, _upperTick);
        if (tokenPosition.pool == address(0x00)) revert WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);

        (amount0, amount1) = pool.collect(
            msg.sender,
            tokenPosition.lowerTick,
            tokenPosition.upperTick,
            params.amount0,
            params.amount1
        );
    }
}
