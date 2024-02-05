// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.14;

import "./Pool.sol";

import "../interface_contracts/IUniswapV3PoolDeployer.sol";

contract PoolFactory is IUniswapV3PoolDeployer {
    error PoolAlreadyExists();
    error ZeroAddressNotAllowed();
    error TokensMustBeDifferent();
    error UnsupportedFee();

    event PoolCreated(
        address indexed token0,
        address indexed token1,
        uint24 indexed fee,
        address pool
    );

    struct CreatedPool {
        address token0;
        address token1;
        uint24 fee;
    }

    PoolParameters public parameters;
    CreatedPool[] public createdPools;

    mapping(uint24 => uint24) public fees;
    mapping(address => mapping(address => mapping(uint24 => address)))
        public pools;

    constructor() {
        fees[500] = 10;
        fees[3000] = 60;
        fees[10000] = 200;
    }

    function getCreatedPools()
        public
        view
        returns (address[] memory, address[] memory, uint24[] memory)
    {
        uint256 arraySize = createdPools.length;

        address[] memory addrsPool0 = new address[](arraySize);
        address[] memory addrsPool1 = new address[](arraySize);
        uint24[] memory poolFees = new uint24[](arraySize);
        for (uint i = 0; i < arraySize; i = i + 1) {
            CreatedPool storage createdpool = createdPools[i];
            addrsPool0[i] = createdpool.token0;
            addrsPool1[i] = createdpool.token1;
            poolFees[i] = createdpool.fee;
        }
        return (addrsPool0, addrsPool1, poolFees);
    }

    function createPool(
        address tokenX,
        address tokenY,
        uint24 fee
    ) public returns (address pool) {
        if (tokenX == tokenY) revert TokensMustBeDifferent();
        if (fees[fee] == 0) revert UnsupportedFee();

        (tokenX, tokenY) = tokenX < tokenY
            ? (tokenX, tokenY)
            : (tokenY, tokenX);

        if (tokenX == address(0)) revert ZeroAddressNotAllowed();
        if (pools[tokenX][tokenY][fee] != address(0))
            revert PoolAlreadyExists();

        parameters = PoolParameters({
            factory: address(this),
            token0: tokenX,
            token1: tokenY,
            tickSpacing: fees[fee],
            fee: fee
        });

        pool = address(
            new Pool{salt: keccak256(abi.encodePacked(tokenX, tokenY, fee))}()
        );

        delete parameters;

        pools[tokenX][tokenY][fee] = pool;
        pools[tokenY][tokenX][fee] = pool;

        createdPools.push(CreatedPool(tokenX, tokenY, fee));
        emit PoolCreated(tokenX, tokenY, fee, pool);
    }
}
