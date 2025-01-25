import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
    // States to store fetched data
    const [funds, setFunds] = useState([]);
    const [balance, setBalance] = useState(null);

    // Fetch financial data and contract balance
    useEffect(() => {
        // Fetch funds overview from the backend API
        const fetchFunds = async () => {
            try {
                const response = await axios.get('/api/funds');
                setFunds(response.data.funds);
            } catch (error) {
                console.error("Error fetching funds:", error);
            }
        };

        // Fetch smart contract balance (replace with actual address)
        const fetchBalance = async () => {
            const address = '0xYourAddressHere'; // Replace with actual address
            try {
                const response = await axios.get(`/api/balance/${address}`);
                setBalance(response.data.balance);
            } catch (error) {
                console.error("Error fetching balance:", error);
            }
        };

        // Trigger both fetch functions
        fetchFunds();
        fetchBalance();
    }, []); // Empty array means this effect will run once on mount

    return (
        <div className="dashboard">
            <h1>Funds Overview</h1>
            
            <section className="funds-section">
                <h2>Current Funds</h2>
                <ul>
                    {funds.length > 0 ? (
                        funds.map((fund, index) => (
                            <li key={index}>
                                {fund.name}: {fund.amount} ETH
                            </li>
                        ))
                    ) : (
                        <p>No funds available.</p>
                    )}
                </ul>
            </section>
            
            <section className="balance-section">
                <h2>Smart Contract Balance</h2>
                <p>{balance ? `${balance} ETH` : 'Loading balance...'}</p>
            </section>

            {/* Optionally, you can add additional sections here */}
        </div>
    );
};

export default Dashboard;

