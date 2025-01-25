import Web3 from 'web3';

// Initialize Web3 with a provider (could be local or through Infura)
const web3 = new Web3('https://base-mainnet.infura.io/v3/05f00595a54449bb9075c44b982bd936');


// Function to get a contract instance
export const getContractInstance = (abi, address) => {
    return new web3.eth.Contract(abi, address);
};

// Function to get the current account address
export const getAccount = async () => {
    const accounts = await web3.eth.getAccounts();
    return accounts[0];  // Return the first account (used for transactions)
};

// Function to send a transaction (example: fund release)
export const sendTransaction = async (contract, method, params) => {
    const account = await getAccount();

    return contract.methods[method](...params).send({ from: account });
};
