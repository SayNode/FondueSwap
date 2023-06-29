// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity ^0.8.14;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "./HelpFunctions.sol";

import "./interfaces/IERC20.sol";
import "./interfaces/IUniswapV3Pool.sol";
import "./lib/LiquidityMath.sol";
import "./lib/NFTRenderer.sol";
import "./lib/TickMath.sol";

contract NFT is ERC721 {
    /*
    Custom Errors
    */
    error NotAuthorized();
    error NotEnoughLiquidity();

    /*
    Events
    */
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

    /*
    Structs
    */
    struct CollectParams {
        uint256 tokenId;
        uint128 amount0;
        uint128 amount1;
    }

    struct AddLiquidityParams {
        uint256 tokenId;
        uint256 amount0Desired;
        uint256 amount1Desired;
        uint256 amount0Min;
        uint256 amount1Min;
    }

    struct RemoveLiquidityParams {
        uint256 tokenId;
        uint128 liquidity;
    }

    /*
    Variables
    */
    uint256 public totalSupply;
    uint256 private nextTokenId;

    address public immutable factory;

    /*
    Mappings
    */
    mapping(uint256 => HelpFunctions.TokenPosition) public positions;
    mapping(address => uint256[]) public userOwnedPositions;
    mapping(uint256 => bool) public burnedIds;

    /*
    Modifiers
    */
    modifier isApprovedOrOwner(uint256 tokenId) {
        address owner = ownerOf(tokenId);
        if (
            msg.sender != owner &&
            !(isApprovedForAll(owner, msg.sender)) &&
            getApproved(tokenId) != msg.sender
        ) revert NotAuthorized();

        _;
    }

    /*
    Constructor
    */
    constructor(address factoryAddress) ERC721("NFT Positions", "PosNFT") {
        factory = factoryAddress;
    }

    /*
    External
    */
    /// @notice Returns a list of all Liquidity Token IDs assigned to an address.
    /// @param _owner The owner whose nfts we are interested in.
    /// @dev This method MUST NEVER be called by smart contract code. First, it's fairly
    ///  expensive (it walks the entire token array looking for tokens belonging to owner),
    ///  but it also returns a dynamic array, which is only supported for web3 calls, and
    ///  not contract-to-contract calls.
    function tokensOfOwner(
        address _owner
    ) public view returns (uint256[] memory ownerTokens) {
        uint256 tokenCount = balanceOf(_owner);

        if (tokenCount == 0) {
            // Return an empty array
            return new uint256[](0);
        } else {
            uint256[] memory result = new uint256[](tokenCount);
            uint256 totalTokens = nextTokenId;
            uint256 resultIndex = 0;

            // We count on the fact that all tokens have IDs starting at 0 and increasing
            // sequentially up to the totalTokens count.
            uint256 tokenId;

            while (resultIndex < totalTokens && tokenId < totalTokens) {
                if (burnedIds[tokenId] != true) {
                    if (ownerOf(tokenId) == _owner) {
                        result[resultIndex] = tokenId;
                        resultIndex++;
                    }
                }
                tokenId++;
            }

            return result;
        }
    }

    /*
    Public 
    */
    /// @notice Used for setting new positions. Mints an NFT connected to the created position
    /// @param params: an array with the following parameters:
    ///             recipient: the user who is minting the new position
    ///             tokenA: first token in the pool where the position is being minted
    ///             tokenB: second token in the pool where the position is being minted
    ///             fee: fee of the pool where the position is being minted
    ///             lowerTick: lower tick of the position being minted
    ///             upperTick: upper tick of the position being minted
    ///             amount0Desired:amount of first token we want to add to the position as liquidity
    ///             amount1Desired:amount of second token we want to add to the position as liquidity
    ///             amount0Min: min amount of first token we want to add to the position as liquidity
    ///             amount1Min: min amount of second token we want to add to the position as liquidity
    function mint(
        HelpFunctions.MintParams calldata params
    ) public returns (uint256 tokenId) {
        IUniswapV3Pool pool = HelpFunctions._getPool(
            factory,
            params.tokenA,
            params.tokenB,
            params.fee
        );

        (uint128 liquidity, uint256 amount0, uint256 amount1) = _addLiquidity(
            HelpFunctions.AddLiquidityInternalParams({
                pool: pool,
                lowerTick: params.lowerTick,
                upperTick: params.upperTick,
                amount0Desired: params.amount0Desired,
                amount1Desired: params.amount1Desired,
                amount0Min: params.amount0Min,
                amount1Min: params.amount1Min
            })
        );

        tokenId = nextTokenId++;

        _mint(params.recipient, tokenId);
        totalSupply++;

        HelpFunctions.TokenPosition memory tokenPosition = HelpFunctions
            .TokenPosition({
                pool: address(pool),
                lowerTick: params.lowerTick,
                upperTick: params.upperTick
            });

        positions[tokenId] = tokenPosition;
        userOwnedPositions[msg.sender].push(tokenId);

        emit AddLiquidity(tokenId, liquidity, amount0, amount1);
    }

    /// @notice Burns an NFT related to a liquidity position
    /// @param tokenId The id of the NFT we wish to burn
    /// @dev This method will fail if called before the user removes all liquidity from the corresponding positions
    ///      and collects the corresponding tokens
    function burn(uint256 tokenId) public isApprovedOrOwner(tokenId) {
        HelpFunctions.TokenPosition memory tokenPosition = positions[tokenId];
        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);
        (uint128 liquidity, , , uint128 tokensOwed0, uint128 tokensOwed1) = pool
            .positions(_poolPositionKey(tokenPosition));

        if (liquidity > 0 || tokensOwed0 > 0 || tokensOwed1 > 0)
            revert HelpFunctions.PositionNotCleared();

        delete positions[tokenId];
        burnedIds[tokenId] = true;
        _burn(tokenId);
        totalSupply--;
    }

    /// @notice collects the tokens relative to a cleared position.
    /// @param params: an array with the following parameters:
    ///             tokenId: the token Id of the position we wish to collect
    ///             amount0: amount of token 0 we want to collect
    ///             amount1: amount of token 1 we want to collect
    /// @dev Can only be called after the user has removed all liquidity from the position
    function collect(
        CollectParams memory params
    )
        public
        isApprovedOrOwner(params.tokenId)
        returns (uint128 amount0, uint128 amount1)
    {
        HelpFunctions.TokenPosition memory tokenPosition = positions[
            params.tokenId
        ];
        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);

        (amount0, amount1) = pool.collect(
            msg.sender,
            tokenPosition.lowerTick,
            tokenPosition.upperTick,
            params.amount0,
            params.amount1
        );
    }

    /// @notice adds liquidity to an existing position.
    /// @param params: an array with the following parameters:
    ///             tokenId: the token Id of the position we wish to add liquidity too
    ///             amount0Desired: amount of token 0 we want to add
    ///             amount1Desired: amount of token 1 we want to add
    ///             amount0Min: min amount of token 0 we want to add
    ///             amount1Min: min amount of token 1 we want to add
    /// @dev does not mint a new NFT. It only updates the position info
    function addLiquidity(
        AddLiquidityParams calldata params
    ) public returns (uint128 liquidity, uint256 amount0, uint256 amount1) {
        HelpFunctions.TokenPosition memory tokenPosition = positions[
            params.tokenId
        ];

        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        (liquidity, amount0, amount1) = _addLiquidity(
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

    /// @notice removes liquidity from an existing position.
    /// @param params: an array with the following parameters:
    ///             tokenId: the token Id of the position we wish to remove liquidity from
    ///             liquidity: the liquidity amount we wish to remove
    /// @dev does not burn the NFT and does not return the tokens to the user (use collect for that).
    ///     It only updates the position info
    function removeLiquidity(
        RemoveLiquidityParams memory params
    )
        public
        isApprovedOrOwner(params.tokenId)
        returns (uint256 amount0, uint256 amount1)
    {
        HelpFunctions.TokenPosition memory tokenPosition = positions[
            params.tokenId
        ];

        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);

        (uint128 availableLiquidity, , , , ) = pool.positions(
            _poolPositionKey(tokenPosition)
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

    /// @notice help function to transfer the tokens.
    function uniswapV3MintCallback(
        uint256 amount0,
        uint256 amount1,
        bytes calldata data
    ) public {
        IUniswapV3Pool.CallbackData memory extra = abi.decode(
            data,
            (IUniswapV3Pool.CallbackData)
        );
        IERC20(extra.token0).transferFrom(extra.payer, msg.sender, amount0);
        IERC20(extra.token1).transferFrom(extra.payer, msg.sender, amount1);
    }

    /*
    Public - View
     */
    /// @notice receives a tokenId and returns all the information regarding that tokens position.
    /// @param tokenId: the token Id
    function tokenIDtoPosition(
        uint256 tokenId
    ) public view returns (address, uint128, uint128, uint128, int24, int24) {
        HelpFunctions.TokenPosition memory tokenPosition = positions[tokenId];
        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);
        (uint128 liquidity, , , uint128 tokensOwed0, uint128 tokensOwed1) = pool
            .positions(_poolPositionKey(tokenPosition));
        return (
            tokenPosition.pool,
            liquidity,
            tokensOwed0,
            tokensOwed1,
            tokenPosition.lowerTick,
            tokenPosition.upperTick
        );
    }

    function userToAllPositions(
        address user
    )
        public
        view
        returns (
            address[] memory,
            uint128[] memory,
            uint128[] memory,
            uint128[] memory,
            int24[] memory,
            int24[] memory
        )
    {
        uint256[] memory _tokensOfOwner = tokensOfOwner(user);
        address[] memory poolAdresses = new address[](_tokensOfOwner.length);
        uint128[] memory liquidities = new uint128[](_tokensOfOwner.length);
        uint128[] memory _tokensOwed0 = new uint128[](_tokensOfOwner.length);
        uint128[] memory _tokensOwed1 = new uint128[](_tokensOfOwner.length);
        int24[] memory lowerTicks = new int24[](_tokensOfOwner.length);
        int24[] memory upperTicks = new int24[](_tokensOfOwner.length);

        for (uint i = 0; i < _tokensOfOwner.length; ++i) {
            HelpFunctions.TokenPosition memory tokenPosition = positions[
                _tokensOfOwner[i]
            ];
            if (tokenPosition.pool == address(0x00))
                revert HelpFunctions.WrongToken();

            IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);
            (
                uint128 liquidity,
                ,
                ,
                uint128 tokensOwed0,
                uint128 tokensOwed1
            ) = pool.positions(_poolPositionKey(tokenPosition));

            poolAdresses[i] = tokenPosition.pool;
            liquidities[i] = liquidity;
            _tokensOwed0[i] = tokensOwed0;
            _tokensOwed1[i] = tokensOwed1;
            lowerTicks[i] = tokenPosition.lowerTick;
            upperTicks[i] = tokenPosition.upperTick;
        }
        return (
            poolAdresses,
            liquidities,
            _tokensOwed0,
            _tokensOwed1,
            lowerTicks,
            upperTicks
        );
    }

    /// @notice returns the URI of the image of an NFT token.
    /// @param tokenId: the token Id
    function tokenURI(
        uint256 tokenId
    ) public view override returns (string memory) {
        HelpFunctions.TokenPosition memory tokenPosition = positions[tokenId];

        if (tokenPosition.pool == address(0x00))
            revert HelpFunctions.WrongToken();

        IUniswapV3Pool pool = IUniswapV3Pool(tokenPosition.pool);

        return
            NFTRenderer.render(
                NFTRenderer.RenderParams({
                    pool: tokenPosition.pool,
                    owner: address(this),
                    lowerTick: tokenPosition.lowerTick,
                    upperTick: tokenPosition.upperTick,
                    fee: pool.fee()
                })
            );
    }

    /*
    Internal
    */
    /// @notice returns position ID within a pool
    /// @param position: an array with the following parameters:
    ///             pool: the token Id
    ///             lowerTick: the token Id
    ///             upperTick: the token Id
    function _poolPositionKey(
        HelpFunctions.TokenPosition memory position
    ) internal view returns (bytes32 key) {
        key = keccak256(
            abi.encodePacked(
                address(this),
                position.lowerTick,
                position.upperTick
            )
        );
    }

    /// @notice help function to add liquidity anytime we mint or add liquidity to an existing position
    function _addLiquidity(
        HelpFunctions.AddLiquidityInternalParams memory params
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
            revert HelpFunctions.SlippageCheckFailed(amount0, amount1);
    }
}
