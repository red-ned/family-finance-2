from fastapi import FastAPI


from ff2.data_base.data_base import DataBase

sessions = dict()

app = FastAPI()

@app.get("/ff2/")
async def get_ff2():
    return {"message": "Welcome to Family Finance 2!"}

@app.get("/ff2/account")
async def get_ff2_accounts():

    db = DataBase('data/ff2_db.db')
    data = db.get_account_options()
    db.close()

    return data

@app.get("/ff2/account/{account_id}")
async def get_ff2_accounts(account_id):

    db = DataBase('data/ff2_db.db')
    data = db.get_account_details(account_id)
    db.close()

    return data

@app.get("/ff2/envelope")
async def get_ff2_envelopes():

    db = DataBase('data/ff2_db.db')
    data = db.get_envelope_options()
    db.close()

    return data

@app.get("/ff2/envelope/{envelope_id}")
async def get_ff2_envelopes(envelope_id):

    db = DataBase('data/ff2_db.db')
    data = db.get_envelope_details(envelope_id)
    db.close()

    return data

@app.get("/ff2/transaction/{transaction_id}")
async def get_ff2_envelopes(transaction_id):

    db = DataBase('data/ff2_db.db')
    data = db.get_transaction_lines(transaction_id)
    db.close()

    return data
