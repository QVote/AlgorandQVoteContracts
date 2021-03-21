""" Queue smart contract.
This smart contract is used by the QVote application to index the latest n decision contracts on the blockchain.
The contract stores n key value pairs containing the addresses to the latest n decision smart contracts.
When a new decision contract's address is pushed, the oldest decision contract gets overridden (unless there are less than n addresses stored in total) """
import sys
from pyteal import *    
    
def approval_program():     
    index_key = Bytes("index")          # the next addressed pushed will have this index
    queue_size_key = Bytes("size")      # maximum number of addresses that can be stored in this queue 
    
    # TODO check validity of queue_size param (must not overflow) 
    on_creation = Seq([    
        App.globalPut(index_key, Int(0)),  
        App.globalPut(queue_size_key, Btoi(Txn.application_args[0])),
        Return(Int(1))
    ])    

    
    on_optin = Return(Int(1))
    
    current_index = App.globalGet(index_key)
    on_push = Seq([    # TODO check that what is pushed is actually and address, or at least has the correct length 
        App.globalPut(Itob(current_index), Txn.application_args[1]), 
        If(App.globalGet(queue_size_key) > current_index+Int(1),    # updating index 
              App.globalPut(index_key, current_index+Int(1)), 
              App.globalPut(index_key, Int(0))),
        Return(Int(1))
    ])

    program = Cond(    
            [Txn.application_id() == Int(0), on_creation],    
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))], 
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],    
            [Txn.on_completion() == OnComplete.OptIn, on_optin],
            [Txn.application_args[0] == Bytes("push"), on_push],
    )    
    return program    
    
    
def clear_state_program():     
    program = Return(Int(1))
    return program    


if __name__ == "__main__":
    teal_dir = "teal/"

    if len(sys.argv) < 2: 
        approval_filename = teal_dir + "queue_approval.teal"
        clear_state_filename = teal_dir + "queue_clear_state.teal"
    else: 
        approval_filename = "teal/" + sys.argv[1]
        clear_state_filename = "teal/" + sys.argv[2]

    # pyteal to teal 
    with open(approval_filename, 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open(clear_state_filename, 'w') as f:
        compiled = compileTeal(clear_state_program(), Mode.Application)
        f.write(compiled)






