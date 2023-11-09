// SPDX-License-Identifier: MIT
// OpenZeppelin Contracts (last updated v4.9.0) (token/ERC721/IERC721.sol)

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

/**
 * @dev Required interface of an ERC721 compliant contract.
 */
interface INFT is IERC721 {
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

    struct TokenPosition {
        address pool;
        int24 lowerTick;
        int24 upperTick;
    }

    function tokenIDtoPosition(
        uint256 tokenID
    ) external view returns (address, int24, int24);
}
