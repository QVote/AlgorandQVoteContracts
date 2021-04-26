# AlgorandQVoteContracts 💎
### [Join our discord!](https://discord.gg/AWt6k9XhpT)
PyTeal Quadratic Voting smart contracts for Algorand

Part of the [Algorand Foundation Grants Program](https://algorand.foundation/grants-program). 💸

## What It Does
These contracts make it simple to do quadratic voting decisions on the Algorand blockchain.

###### &nbsp;&nbsp;&nbsp;&nbsp; 🌍 &nbsp; Support for positive and negative credit distributions (true quadratic voting).
######  &nbsp;&nbsp;&nbsp;&nbsp; 🔒 &nbsp; Voting power dependent on usre's ownerships of a given Algorand Standard Asset.
###### &nbsp;&nbsp;&nbsp;&nbsp; 🗄️ &nbsp; Store references to decisions in the Queue smart contract for increased accessibility.
######  &nbsp;&nbsp;&nbsp;&nbsp; 🕐 &nbsp; Decisions divided in two distinct time-phases: registration and voting.

# Contracts :scroll:
Contracts are located in: /contracts

There are 2 PyTeal contracts:
- Queue.py (a queue for storing contract addresses)
- QuadraticVoting.py (quadratic voting logic)

Running the files will compile the contracts to ```.teal``` in ```contracts/teal/``` :
```bash
python QuadraticVoting.py && python Queue.py
```

### QVoting :heart:
This is the quadratic voting contract. Each deployed contract represents one decision. This gets populated with options at creation (up to 5 options), if you want more options you can add them after creation (again, 5 at a time). Rigth after creation the registration period starts, during which voters sign up to vote and receive their credits, based on their balance in the ASA set in the contract. Once the registation period is over, the voting starts. You can then cast votes with quadratic cost by sending a tx to the smart contract, one option at a time. 

### DecisionQueue :post_office:
This smart contract is simply a reference to the 'up to 61 latest' decision smart contracts. The contracts referenced here are to be posted on the web app using the contracts. If you want to create an election and NOT have it be displayed on the web app, don't register it in the queue. 

# Walkthrough 🤓
For the full code go to /notebooks and play around with the contracts yourself!

### Deploying :airplane:
Let's set the asset that dictates voting power of our voters. In this case, the amount of credits you get is 2 times however many of asset 13164495 you own, which is a dummy asset we made. 
```python 
asset_id = 13164495    # this asset is used to compare 
asset_coefficient = 2    # how many voting coins you get for each token of the asset you own 
```

Compile or load the approval program and clear state bytes. Then set all the election's parameters. Make sure you update the local schema: each option will be a separate key-value pair. 
```python
approval_bytes, clear_state_bytes = compile()

decision_name = 'muchdecision'

local_schema = StateSchema(num_uints=1, num_byte_slices=1)    
global_schema = StateSchema(num_uints=61, num_byte_slices=3)     # maximum sum is 64

registration_seconds = 300
voting_seconds = 300

start_time = round(time.time()) + registration_seconds
end_time = start_time + voting_seconds
```
This is a standard ApplicationCreate transaction. On creation we can set up to 5 options in the smart contract. If you want to set less than 5 you have to 'pad' the rest with 'NULL_OPTION', a symbol recognized by the smart contract. 
``` python
on_complete = onComplete(0)
app_create_txn = transaction.ApplicationCreateTxn(
    funded_accounts[4]['pk'], 
    params, 
    on_complete, 
    approval_bytes, 
    clear_state_bytes, 
    global_schema, 
    local_schema,
    # you always need to submit this many options. you can use NULL_OPTION to ingore an option 
    app_args = [decision_name.encode('utf-8'), 
                "first".encode('utf-8'),
                "second".encode('utf-8'),
                "third".encode('utf-8'), 
                "NULL_OPTION".encode('utf-8'),
                "NULL_OPTION".encode('utf-8'), 
                asset_id.to_bytes(3, 'big'),
                asset_coefficient.to_bytes(2, 'big'), 
                start_time.to_bytes(6, 'big'),
                end_time.to_bytes(6, 'big')]
)

app_create_txn_signed = app_create_txn.sign(funded_accounts[4]['sk'])
txid = algod_client.send_transaction(app_create_txn_signed)
```
Get the app-id to interact with the contract 
```python 
app_id = algod_client.pending_transaction_info(txid)['application-index']
```

At this point the contract state should look something like this. The keys have been decoded for better readibility. Keys corresponding to options you can vote for have the 'options_' prefix. 
```python
[[{'key': 'option_third',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775808}},
  {'key': 'voting_end_time',
   'value': {'bytes': '', 'type': 2, 'uint': 1616422316}},
  {'key': 'option_second',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775808}},
  {'key': 'Creator',
   'value': {'bytes': 'hmXzebxJfQ9OITtFlPuRxlG9X6Sb/YeOo4wVxBw0Bh0=',
    'type': 1,
    'uint': 0}},
  {'key': 'Name',
   'value': {'bytes': 'bXVjaGRlY2lzaW9u', 'type': 1, 'uint': 0}},
  {'key': 'option_first',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775808}},
  {'key': 'voting_start_time',
   'value': {'bytes': '', 'type': 2, 'uint': 1616422016}},
  {'key': 'asset_id', 'value': {'bytes': '', 'type': 2, 'uint': 13164495}},
  {'key': 'asset_coefficient', 'value': {'bytes': '', 'type': 2, 'uint': 2}}]]
```
### Adding options :heavy_plus_sign:
In case you want to have more than 5 options in your decisions, you can add them later. Again, 5 at a time, and you have to pad them with 'NULL_OPTION'. 
```python
def add_options_tx(option_names, sender=4):
    app_args = ["add_options".encode("utf-8")] + [option_name.encode('utf-8') for option_name in option_names]

    # create unsigned transaction
    call_tx = transaction.ApplicationNoOpTxn(funded_accounts[sender]['pk'], params, app_id, app_args)
    call_txid = algod_client.send_transaction(call_tx.sign(funded_accounts[sender]['sk']))
    return call_txid

call_txid = add_options_tx(["new_one", "new_two", "new_three", "new_four", "NULL_OPTION"])
```

### Opting in
This is pretty standard. You can only opt in the registration phase, so before the voting starts. When you do this the contract checks your balance in the above mentioned ASA and assigns you credits. Your credits will be stored in your account's local storage. 
```
optin_tx = transaction.ApplicationOptInTxn(funded_accounts[2]['pk'], params, app_id)
algod_client.send_transaction(optin_tx.sign(funded_accounts[2]['sk']))
```

### Voting :speaking_head:
Here's what you came for. You can vote quadratically on the options, one at a time. You will have to pass '-' as sign if you want to vote negatively (yes you can), anything else will vote positively. 
```python 
# negative vote
option_name = "first"
votes = 3
sign = "-"
app_args = ["vote".encode("utf-8"), option_name.encode("utf-8"), votes.to_bytes(2, "big"), sign.encode("utf-8")]

# create unsigned transaction
call_tx = transaction.ApplicationNoOpTxn(funded_accounts[2]['pk'], params, app_id, app_args)
call_txid = algod_client.send_transaction(call_tx.sign(funded_accounts[2]['sk']))
```
Now the contract state will look like this. If you notice, votes talleis don't start at 0. This is to pretend we have negative numbers. 0 is actually represented as 9223372036854775808. So 9223372036854775805 for the option 'first' actually means -3 votes. 
```python
[[{'key': 'voting_end_time',
   'value': {'bytes': '', 'type': 2, 'uint': 1616421504}},
  {'key': 'option_first',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775805}},
  {'key': 'option_second',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775808}},
  {'key': 'asset_id', 'value': {'bytes': '', 'type': 2, 'uint': 13164495}},
  {'key': 'option_third',
   'value': {'bytes': '', 'type': 2, 'uint': 9223372036854775808}},
  {'key': 'asset_coefficient', 'value': {'bytes': '', 'type': 2, 'uint': 2}},
  {'key': 'voting_start_time',
   'value': {'bytes': '', 'type': 2, 'uint': 1616421504}},
  {'key': 'Creator',
   'value': {'bytes': 'hmXzebxJfQ9OITtFlPuRxlG9X6Sb/YeOo4wVxBw0Bh0=',
    'type': 1,
    'uint': 0}},
  {'key': 'Name',
   'value': {'bytes': 'bXVjaGRlY2lzaW9u', 'type': 1, 'uint': 0}}]]
```

```python
# positive vote 
option_name = "first"
votes = 5
sign = "+"
app_args = ["vote".encode("utf-8"), option_name.encode("utf-8"), votes.to_bytes(2, "big"), sign.encode("utf-8")]

# create unsigned transaction
call_tx = transaction.ApplicationNoOpTxn(funded_accounts[2]['pk'], params, app_id, app_args)
call_txid = algod_client.send_transaction(call_tx.sign(funded_accounts[2]['sk']))
```



## Possible extensions:
- [ ] Add quadratic funding on top of QVoting contract
- [ ] QVote with NFTs. This would actually make credit checking and double voting prevention much easier. Idea is "if you have this NFT you have this amount of credits available to you" 
