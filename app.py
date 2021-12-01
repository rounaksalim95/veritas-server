# from solc import compile_files

# contracts = compile_files(["../contracts/veritas.sol"])

# contract_id, contract_interface = contracts.popitem()

# bytecode = contract_interface["bin"]

# abi = contract_interface["abi"]

import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3

app = Flask(__name__)
CORS(app)

# DB
users = {}
companies = {}
company_name_map = {}


# Flask routes
@app.route("/signup/customer", methods=["POST"])
def sign_up_customer():
    request_data = request.json
    username = request_data["username"]
    password = request_data["password"]
    users[username] = password
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
    company_name_map[username] = request_data["name"]
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
        return jsonify({"message": "Invalid username"}), 400

    if username in companies:
        company_name = company_name_map[username]
        # return hardcoded products for now
        return jsonify(
            {
                "message": "Company found",
                "company_name": company_name,
                "products": [
                    {
                        "name": "Nike Shoes 0",
                        "description": "Nike Air Force 1",
                        "sku": 24,
                        "id": 23,
                    },
                    {
                        "name": "Nike Shoes 1",
                        "description": "Nike Air Force 1",
                        "sku": 2434,
                        "id": 23245,
                    },
                ],
            }
        )
    else:
        return jsonify({"message": "Company not found for " + username}), 404


@app.route("/sell/product", methods=["POST"])
def sell_product():
    request_data = request.json
    username = request_data["username"]
    new_owner = request_data["new_owner"]  # New owner's email address
    product_id = request_data["product_id"]

    return jsonify({"message": "Product sold successfully to " + new_owner})


@app.route("/transfer/product", methods=["POST"])
def transfer_product():
    request_data = request.json
    username = request_data["username"]
    new_owner = request_data["new_owner"]  # New owner's email address
    product_id = request_data["product_id"]

    return jsonify({"message": "Product transferred successfully to " + new_owner})


if __name__ == "__main__":
    app.run(debug=True)
