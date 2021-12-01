def get_products(contract, address):
    products = []
    _products = contract.functions.getAllProducts(address).call()
    for product in _products:
        products.append(
            {
                "name": product[0],
                "description": product[1],
                "sku": product[2],
                "product_id": product[3],
                "manufacturer_address": product[4],
                "owner": product[5],
            }
        )

    return products


def add_product(w3, contract, name, description, sku, company_address, p_key):
    nonce = w3.eth.getTransactionCount(company_address)
    transaction = contract.functions.createProduct(
        name, description, sku, company_address
    ).buildTransaction(
        {
            "gas": 700000,
            "gasPrice": w3.toWei("200", "gwei"),
            "from": company_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=p_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)


def transfer_product(w3, contract, product_id, from_address, to_address, p_key):
    nonce = w3.eth.getTransactionCount(from_address)
    transaction = contract.functions.transferProduct(
        product_id, to_address
    ).buildTransaction(
        {
            "gas": 700000,
            "gasPrice": w3.toWei("200", "gwei"),
            "from": from_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=p_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
