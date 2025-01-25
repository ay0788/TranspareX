import Web3 from 'web3';

const web3 = new Web3(Web3.givenProvider || 'http://localhost:8545');
export const getContractInstance = (abi, address) => new web3.eth.Contract(abi, address);
