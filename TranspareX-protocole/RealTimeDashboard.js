import React, { useState, useEffect } from 'react';
import Web3 from 'web3';

// Helper function to initialize the contract instance
const getContractInstance = (abi, address) => {
    const web3 = new Web3('ws://127.0.0.1:7545'); // Ganache WebSocket URL
    return new web3.eth.Contract(abi, address);
};

const RealTimeDashboard = () => {
    const [transactions, setTransactions] = useState([]);
    const [fundReleaseStatus, setFundReleaseStatus] = useState(null);

    useEffect(() => {
        // Contract details from your Ganache setup
        const contractAddress = '0x9b64DE133BAb117b4F37cf7fE239BF5e4C062aeD'; // Replace with your deployed contract address
        const abi = [
            {
                "inputs": [
                    { "internalType": "address", "name": "recipient", "type": "address" },
                    { "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "name": "releaseFunds",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": false,
                "inputs": [
                    { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" },
                    { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" }
                ],
                "name": "FundReleased",
                "type": "event"
            }
        ]; // Replace with the full ABI of your contract
        const contract = getContractInstance(abi, contractAddress);

        // Listen for "FundReleased" events from the contract
        const eventListener = contract.events.FundReleased({
            fromBlock: 'latest', // Listen from the latest block
        })
            .on('data', (event) => {
                const { returnValues } = event;
                // Update state with the new transaction data
                setTransactions((prev) => [
                    ...prev,
                    {
                        txHash: event.transactionHash,
                        recipient: returnValues.recipient,
                        amount: Web3.utils.fromWei(returnValues.amount, 'ether'), // Convert amount to ETH
                        timestamp: new Date().toLocaleString(),
                    },
                ]);
                setFundReleaseStatus('Funds released successfully');
            })
            .on('error', (error) => {
                console.error('Error fetching event data', error);
            });

        // Cleanup function to remove listeners when the component unmounts
        return () => {
            eventListener.off();
        };
    }, []);

    return (
        <div className="real-time-dashboard">
            <h1>Real-Time Fund Updates</h1>
            
            <section className="status-section">
                <h2>Status</h2>
                <p>{fundReleaseStatus || 'Waiting for updates...'}</p>
            </section>
            
            <section className="transactions-section">
                <h2>Recent Transactions</h2>
                {transactions.length > 0 ? (
                    <ul>
                        {transactions.map((tx, index) => (
                            <li key={index}>
                                <p><strong>Transaction Hash:</strong> {tx.txHash}</p>
                                <p><strong>Recipient:</strong> {tx.recipient}</p>
                                <p><strong>Amount:</strong> {tx.amount} ETH</p>
                                <p><strong>Time:</strong> {tx.timestamp}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No transactions yet.</p>
                )}
            </section>
        </div>
    );
};

export default RealTimeDashboard;
