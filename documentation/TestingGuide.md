# Testing Guide

## Brownie

Each test should be run separately.
Simply install Brownie and to

> brownie test tests\<name_of_test>.py

## Vechain

Add the _contracts_, _interface_contracts_ and _lib_ from this directory, to the workspace in the [Vechain Energy IDE](https://ide.vechain.energy/).
Compile the relevant contracts (MockToken, PoolFactory, NFT and SwapManager) and , using the _At Address_ button and the addresses in _Tests.md_, import the already deployed contracts. After this you are free to try any function (remember to fund your wallet with the two tokens)
