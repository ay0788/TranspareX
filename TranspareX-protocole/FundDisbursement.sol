// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FundManagement {
    address public owner;
    mapping(address => uint256) public balances;
    mapping(address => uint256) public fundsReleased;
    
    event FundsDeposited(address indexed sender, uint256 amount);
    event FundsReleased(address indexed recipient, uint256 amount);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // Deposit funds to the contract
    function deposit() external payable {
        require(msg.value > 0, "Deposit amount must be greater than zero");
        balances[msg.sender] += msg.value;
        emit FundsDeposited(msg.sender, msg.value);
    }

    // Release funds to a specified recipient
    function releaseFunds(address payable recipient, uint256 amount) external onlyOwner {
        require(balances[owner] >= amount, "Insufficient funds in the contract");
        require(amount > 0, "Amount must be greater than zero");
        
        balances[owner] -= amount;
        recipient.transfer(amount);
        
        fundsReleased[recipient] += amount;
        emit FundsReleased(recipient, amount);
    }

    // Get the balance of the contract
    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }

    // Get the balance of an address
    function getBalance(address account) external view returns (uint256) {
        return balances[account];
    }
}
