# AlgorandQVoteContracts 💎
PyTeal Quadratic Voting smart contracts for Algorand

Part of the [Algorand Foundation Grants Program](https://algorand.foundation/grants-program). 💸

## What It Does
These contracts make it simple to do quadratic voting decisions on the Algorand blockchain.

###### &nbsp;&nbsp;&nbsp;&nbsp; 🌍 &nbsp; Support for positive and negative credit distributions (true quadratic voting).
######  &nbsp;&nbsp;&nbsp;&nbsp; 🔒 &nbsp; Voters can vote depending on their stake in a given Algorand asset.
###### &nbsp;&nbsp;&nbsp;&nbsp; 🗄️ &nbsp; Store references to decisions in the Queue smart contract for increased accessibility.
######  &nbsp;&nbsp;&nbsp;&nbsp; 🕐 &nbsp; Decisions have a registration period, start time and end time.

# Contracts :scroll:
Contracts are located in: /contracts

There are 2 PyTeal contracts:
- Queue.py (a queue for storing contract addresses)
- QuadraticVoting.py (quadratic voting logic)

Those get compiled down to teal to /contracts/teal/ just by runnning the files:
```bash
python QuadraticVoting.py && python Queue.py
```

### QVoting
This is the real quadratic voting contract. Each contract represents one decision. This gets populated with options at creation (up to 5 options), if you want more options you can add them after creation. Rigth after creation the registration period starts, during which voters sign up to vote and receive their credits, based on the token set in the contract. Once the registation period is over, the voting starts. Casting your vote is done by sending a tx to the decision contract, which will check your balance again, making sure you didn't move your tokens (you can't move tokens to a new account and register twice...). 

### DecisionQueue
This smart contract is simply a reference to the 'up to 61 latest' decision smart contracts. The contracts referenced here are to be posted on the web app using the contracts. If you want to create an election and NOT have it be displayed on the web app, don't register it in the queue. 

# Demo 🤓
Go to /notebooks

And play around with the contracts yourself!

# Tests :test_tube:
# FILL THIS IN

## Possible extensions:
- [ ] Add quadratic funding on top of QVoting contract
- [ ] QVote with NFTs. This would actually make credit checking and double voting prevention much easier. Idea is "if you have this NFT you have this amount of credits available to you" 
