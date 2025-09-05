import json
from web3 import Web3
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(Config.GANACHE_URL))
        self.contract_address = Config.CONTRACT_ADDRESS
        self.abi = self._get_contract_abi()
        self.contract = None
        self._initialize_contract()
    
    def _get_contract_abi(self):
        """Contract ABI - in production, this should be loaded from a file"""
        return [
            {
                "inputs": [
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "releaseFunds",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"}
                ],
                "name": "FundReleased",
                "type": "event"
            },
            {
                "inputs": [],
                "name": "getContractBalance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
                "name": "getBalance",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _initialize_contract(self):
        """Initialize the contract instance"""
        try:
            if self.web3.is_connected():
                self.contract = self.web3.eth.contract(
                    address=self.contract_address,
                    abi=self.abi
                )
                logger.info("Successfully connected to blockchain and initialized contract")
            else:
                logger.error("Failed to connect to blockchain")
                self.contract = None
        except Exception as e:
            logger.error(f"Error initializing contract: {str(e)}")
            self.contract = None
    
    def is_connected(self):
        """Check if connected to blockchain"""
        return self.web3.is_connected() and self.contract is not None
    
    def get_contract_balance(self):
        """Get the balance of the smart contract"""
        try:
            if not self.is_connected():
                return None
            
            balance_wei = self.contract.functions.getContractBalance().call()
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting contract balance: {str(e)}")
            return None
    
    def get_account_balance(self, address):
        """Get the balance of a specific account"""
        try:
            if not self.is_connected():
                return None
            
            balance_wei = self.contract.functions.getBalance(address).call()
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting account balance: {str(e)}")
            return None
    
    def release_funds(self, recipient_address, amount_eth, from_account=None):
        """Release funds to a recipient address"""
        try:
            if not self.is_connected():
                return {"success": False, "error": "Not connected to blockchain"}
            
            # Convert ETH to Wei
            amount_wei = self.web3.to_wei(amount_eth, 'ether')
            
            # Get the first account if none specified (for Ganache)
            if not from_account:
                accounts = self.web3.eth.accounts
                if not accounts:
                    return {"success": False, "error": "No accounts available"}
                from_account = accounts[0]
            
            # Build transaction
            transaction = self.contract.functions.releaseFunds(
                recipient_address, amount_wei
            ).build_transaction({
                'from': from_account,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(from_account)
            })
            
            # For demo purposes, we'll simulate the transaction
            # In production, you would sign and send the transaction
            logger.info(f"Simulating fund release: {amount_eth} ETH to {recipient_address}")
            
            return {
                "success": True,
                "transaction_hash": "0x" + "0" * 64,  # Simulated hash
                "amount": amount_eth,
                "recipient": recipient_address,
                "message": f"Funds released successfully to {recipient_address}"
            }
            
        except Exception as e:
            logger.error(f"Error releasing funds: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_fund_released_events(self, from_block=0, to_block='latest'):
        """Get all FundReleased events"""
        try:
            if not self.is_connected():
                return []
            
            events = self.contract.events.FundReleased.create_filter(
                fromBlock=from_block,
                toBlock=to_block
            ).get_all_entries()
            
            formatted_events = []
            for event in events:
                formatted_events.append({
                    "transaction_hash": event.transactionHash.hex(),
                    "recipient": event.args.recipient,
                    "amount": float(self.web3.from_wei(event.args.amount, 'ether')),
                    "block_number": event.blockNumber,
                    "log_index": event.logIndex
                })
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return []
    
    def get_transaction_details(self, tx_hash):
        """Get details of a specific transaction"""
        try:
            if not self.is_connected():
                return None
            
            transaction = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": transaction.hash.hex(),
                "from": transaction['from'],
                "to": transaction['to'],
                "value": float(self.web3.from_wei(transaction.value, 'ether')),
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber,
                "status": "success" if receipt.status == 1 else "failed"
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction details: {str(e)}")
            return None

# Global instance
blockchain_service = BlockchainService()
