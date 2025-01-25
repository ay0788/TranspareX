from flask import Flask, jsonify, request
from web3 import Web3
import json
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Use the Ganache URL (make sure it's the same URL as in your Ganache app)
ganache_url = "http://127.0.0.1:7545"  # Update with your Ganache URL
web3 = Web3(Web3.HTTPProvider(ganache_url))

if web3.is_connected():
    print("Connected to Ganache")
else:
    print("Unable to connect to Ganache")

# Contract details
contract_address = '0x9b64DE133BAb117b4F37cf7fE239BF5e4C062aeD'  
abi = json.loads('''[
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "address",
                "name": "recipient",
                "type": "address"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "name": "FundReleased",
        "type": "event"
    }
]''') 

# Initialize the contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Routes
@app.route("/")
def index():
    return jsonify({"message": "Welcome to TranspareX!"})

@app.route("/funds", methods=["GET"])
def get_funds():
    try:
        # Fetch recent transactions
        return jsonify({"message": "No data to fetch for funds yet"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/events", methods=["GET"])
def get_events():
    try:
        # Fetch all "FundReleased" events
        latest_block = web3.eth.block_number
        events = contract.events.FundReleased.create_filter(
            fromBlock=0, toBlock=latest_block
        ).get_all_entries()

        response = []
        for event in events:
            response.append({
                "transactionHash": event.transactionHash.hex(),
                "recipient": event.args.recipient,
                "amount": event.args.amount
            })

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/release-funds", methods=["POST"])
def release_funds():
    try:
        data = request.json
        recipient = data.get("recipient")
        amount = data.get("amount")

        if not recipient or not amount:
            return jsonify({"error": "Recipient and amount are required"}), 400

        print(f"Simulating fund release to {recipient} of amount {amount}")
        return jsonify({"message": f"Funds released to {recipient} of {amount} ETH"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# New route to get transaction details
@app.route("/transaction/<tx_hash>", methods=["GET"])
def get_transaction(tx_hash):
    try:
        # Fetch transaction details by hash
        transaction = web3.eth.getTransaction(tx_hash)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        
        # Create response object with transaction details
        response = {
            "transactionHash": transaction.hash.hex(),
            "recipient": transaction.to,
            "amount": web3.fromWei(transaction.value, 'ether'),  # Convert Wei to Ether
            "status": "Success"  # You can update this based on the transaction status
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
