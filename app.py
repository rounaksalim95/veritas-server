import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3

import blockchain_utils

app = Flask(__name__)
CORS(app)

# DB
users = {}
companies = {}
company_name_map = {}
users_name_map = {}

accounts = [
    "0x6c655f7A69B42B7697018F5F0001aB44BFd8F07e",
    "0x07784e93c7f59bf9bc3faEA6DbE2bD4c2A350975",
    "0x4E26A6e5d794c7C64D4dC7B373FA552353b63Ab8",
    "0xdE1fa04aB7E72AA3352BE3e512A60BE52ED69c48",
    "0x37a4037F2757253E9453bDBc7947d8dC23e6BCbD",
    "0x9A890360017bc5978dc703A917a6d9aEb1e06f70",
    "0x6C6aFd999d84FCFeeaee077d3b80a0c7adAD45ab",
    "0x29fAe940b19dC1d5b147A5034eE778B431A4504b",
    "0x618d8712CA453f5C241344E5a518122F61c2E1D4",
    "0x5fCD8aD419f78C2b7A72ab73A22BD28f4B00427E",
    "0xC161a24D0D6b642a0B674097a400d696eeaBbA0c",
    "0xDF145Cea053a35B7d70fdCb124af67AEed922088",
    "0xc8A16495f3E047EA48240ed8849A65Fef37cA75a",
]
keys = [
    "0x39ca563ef3529983b0e5fe59f3c137b6324a71c1e1677993e49405cfd50544e1",
    "0xc54bdb6d9d92c5e9044a252d46e37f97e20e51c7332ae1b73a13a5d47e99ca5a",
    "0xda1e3a1fb3cc532b885af78e0bbcc28dbe43c38155d1e5bcb52133bf54c469fc",
    "0x7f2d1385780845bb0917365fa1f789f8063953244676a08ea64118358308b89c",
    "0xe4baa2996f7b7d3515c1f3f07e28c54ab49ee16029e1907fabf2c97f091db85c",
    "0xd885d08976adcec02093012c5284229de7068267910b6310881b40aa36449025",
    "0x69a1b7bae7ca5841a39fe255f4e69352fc2624b324ccc172bf1760cba7be16b9",
    "0xef238e2fd7ac8835bf9e6f8260cf84f8e99931eac4038819b201ad34f7f40ef2",
    "0x096a56e36b5d7e20cf0af268ec2747668234ea79b67b54b320a8f975cdfa1657",
    "0x334fb8a070236e58b56a9d08626bf64fca888b41981c95317967ea20db7feb07",
    "0x38ade19aba79d85e073f4901394c6002083639d28a211e43067071908b7e853a",
    "0x7805323a4a079b2dd2ed8ef067ffd063a2705c893bb91e16bc44e70ab2426699",
    "0x510c4aa78a41b3e7295c59c274864a5bc216ab0537731e393dbd0940a8656541",
]

solc_output = ""

try:
    with open("./combined.json") as json_file:
        solc_output = json.load(json_file)
except Exception as e:
    print("Error opening JSON output file")
    print(e)

contract_data = solc_output["contracts"]["veritas.sol:Veritas"]
abi = contract_data["abi"]

contract_address = Web3.toChecksumAddress("0x73d810bd0ce91eb77ce3ac983f64b2E00a6D1d90")

w3 = Web3(
    Web3.HTTPProvider("https://ropsten.infura.io/v3/ebd7954686ad408eab72c329eeacd8ae")
)

print(w3.isConnected())

contract = w3.eth.contract(address=contract_address, abi=abi)


# Flask routes
@app.route("/signup/customer", methods=["POST"])
def sign_up_customer():
    request_data = request.json
    username = request_data["username"]
    password = request_data["password"]
    users[username] = password

    print("\n Signing up customer with request data:", request_data)

    if len(accounts) <= 0:
        return jsonify({"message": "Error creating account - out of resources"}), 400

    account = accounts.pop()
    p_key = keys.pop()

    users_name_map[username] = (account, p_key)

    return jsonify({"message": "Customer created successfully"})


@app.route("/signin/customer", methods=["POST"])
def sign_in_customer():
    request_data = request.json
    if (
        request_data["username"] in users
        and users[request_data["username"]] == request_data["password"]
    ):
        return jsonify({"message": "Customer successfully authenticated"})
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@app.route("/signup/company", methods=["POST"])
def sign_up_company():
    request_data = request.json
    username = request_data["username"]
    password = request_data["password"]
    companies[username] = password

    print("\n Signing up company with request data:", request_data)

    if len(accounts) <= 0:
        return jsonify({"message": "Error signing up company - out of resources"}), 400

    company_address = accounts.pop()
    company_key = keys.pop()

    company_name_map[username] = (request_data["name"], company_address, company_key)
    return jsonify({"message": "Company created successfully"})


@app.route("/signin/company", methods=["POST"])
def sign_in_company():
    request_data = request.json
    if (
        request_data["username"] in companies
        and companies[request_data["username"]] == request_data["password"]
    ):
        return jsonify({"message": "Company successfully authenticated"})
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@app.route("/company/<username>", methods=["GET"])
def get_company_information(username):
    if username == "" or username is None:
        return jsonify({"message": "Invalid username for company"}), 400

    print("\nProviding company information for " + username)

    if username in companies:
        company_name = company_name_map[username][0]
        company_address = company_name_map[username][1]

        try:
            products = blockchain_utils.get_products(contract, company_address)
        except Exception as e:
            print("Error getting products from blockchain")
            print(e)

        return jsonify(
            {
                "message": "Company found",
                "company_name": company_name,
                "products": products,
            }
        )
    else:
        return jsonify({"message": "Company not found for " + username}), 404


@app.route("/customer/<username>", methods=["GET"])
def get_customer_information(username):
    if username == "" or username is None:
        return jsonify({"message": "Invalid username for customer"}), 400

    print("\nProviding customer information for " + username)

    if username in users:
        user_address = users_name_map[username][0]

        try:
            products = blockchain_utils.get_products(contract, user_address)
        except Exception as e:
            print("Error getting products from blockchain")
            print(e)

        return jsonify(
            {
                "message": "Customer found",
                "products": products,
            }
        )
    else:
        return jsonify({"message": "Customer not found for " + username}), 404


@app.route("/company/add/product", methods=["POST"])
def add_product():
    request_data = request.json
    username = request_data["username"]
    product_name = request_data["product_name"]
    product_description = request_data["product_description"]
    product_sku = request_data["product_sku"]

    print("\nAdding product with request data:", request_data)

    try:
        blockchain_utils.add_product(
            w3,
            contract,
            product_name,
            product_description,
            product_sku,
            company_name_map[username][1],
            company_name_map[username][2],
        )
    except Exception as e:
        print("Error adding product to blockchain")
        print(e)
        return jsonify({"message": "Error adding product to blockchain"}), 400

    return jsonify({"message": "Product added successfully"})


@app.route("/sell/product", methods=["POST"])
def sell_product():
    request_data = request.json
    username = request_data["username"]
    new_owner = request_data["new_owner"]  # New owner's email address
    product_id = request_data["product_id"]

    print("\nSelling product with request data:", request_data)

    if not new_owner in users:
        return (
            jsonify({"message": "Account you're sending the token to doesn't exist"}),
            400,
        )

    try:
        blockchain_utils.transfer_product(
            w3,
            contract,
            product_id,
            company_name_map[username][1],
            users_name_map[new_owner][0],
            company_name_map[username][2],
        )
    except Exception as e:
        print("Error transferring token on blockchain")
        print(e)
        return (
            jsonify(
                {"message": "Error transferring token on blockchain while selling"}
            ),
            400,
        )

    return jsonify({"message": "Product sold successfully to " + new_owner})


@app.route("/transfer/product", methods=["POST"])
def transfer_product():
    request_data = request.json
    username = request_data["username"]
    new_owner = request_data["new_owner"]  # New owner's email address
    product_id = request_data["product_id"]

    print("\nTransferring product with request data:", request_data)

    if not new_owner in users:
        return (
            jsonify({"message": "Account you're sending the token to doesn't exist"}),
            400,
        )

    try:
        blockchain_utils.transfer_product(
            w3,
            contract,
            product_id,
            users_name_map[username][0],
            users_name_map[new_owner][0],
            users_name_map[username][1],
        )
    except Exception as e:
        print("Error transferring token on blockchain")
        print(e)
        return jsonify({"message": "Error transferring token on blockchain"}), 400

    return jsonify({"message": "Product transferred successfully to " + new_owner})


@app.route("/company/<username>/keys", methods=["GET"])
def get_company_keys(username):
    if username == "" or username is None:
        return jsonify({"message": "Invalid username for company"}), 400

    print("\nGetting keys for company:", username)

    if username in companies:
        return jsonify(
            {
                "message": "Company found",
                "public_key": company_name_map[username][1],
                "private_key": company_name_map[username][2],
            }
        )
    else:
        return jsonify({"message": "Company not found for " + username}), 404


@app.route("/customer/<username>/keys", methods=["GET"])
def get_customer_keys(username):
    if username == "" or username is None:
        return jsonify({"message": "Invalid username for customer"}), 400

    print("\nGetting keys for customer:", username)

    if username in users:
        return jsonify(
            {
                "message": "Company found",
                "public_key": users_name_map[username][0],
                "private_key": users_name_map[username][1],
            }
        )
    else:
        return jsonify({"message": "Customer not found for " + username}), 404


@app.route("/test", methods=["GET"])
def test():
    print("\nTesting the app")
    return jsonify({
        "users": users,
        "companies": companies,
        "users_name_map": users_name_map,
        "company_name_map": company_name_map,
    })


if __name__ == "__main__":
    app.run(debug=True)
