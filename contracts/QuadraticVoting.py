import sys
from pyteal import *    
    
def approval_program():     
    VOTING_CREDIT_SYM = Bytes("QVoteDecisionCredits")
    OPTION_PREFIX = Bytes("option_")
    NULL_OPTION = Bytes("NULL_OPTION")
    ZERO = Int(2**63)     # to have neative numbers 
    MINUS = Bytes("-")
    
    arg_num = Txn.application_args.length()
    
    on_closeout = Return(Int(1))
    
    asset_id = App.globalGet(Bytes("asset_id"))
    asset_balance = AssetHolding.balance(Int(0), asset_id) 
    asset_coeff = App.globalGet(Bytes("asset_coefficient"))
    on_optin = Seq([     # TODO if not before voting start time 
        asset_balance, 
        If(asset_balance.hasValue(),  # if sender has some tokens, store it, otherwise return 0     
           Seq([App.localPut(Int(0), VOTING_CREDIT_SYM, Mul(asset_balance.value(), asset_coeff)), Return(Int(1))]),      
           Return(Int(0))
        ) 
    ])  
    
    # TODO registration time 
    option0 = Concat(OPTION_PREFIX, Txn.application_args[1])
    option0_tally = App.globalGetEx(Int(0), option0)            # current total of votes for this option
    option0_votes = Btoi(Txn.application_args[2])               # how much the user wants to vote for this option 
    option0_votes_sign = Txn.application_args[3]
    credit_balance = App.localGet(Int(0), VOTING_CREDIT_SYM)
    on_vote = Seq([ 
        option0_tally, 
        If(option0_tally.hasValue(),      # if user chose a valid option 
           Seq([
               App.localPut(Int(0), VOTING_CREDIT_SYM, credit_balance-Mul(option0_votes, option0_votes)),     # update balance
               If(Ge(credit_balance, Int(0)),             # does credit_balance this get re-evaluated? 
                    If(option0_votes_sign == MINUS,
                       App.globalPut(option0, option0_tally.value()-option0_votes),    
                       App.globalPut(option0, option0_tally.value()+option0_votes), 
                      ),
                    Return(Int(0))
                 ),    
               Return(Int(1))
           ]),
           Return(Int(0))
          )
    ])
    
    
    # add up to 5 options at a time. 
    on_add_options =  Seq([
        If(Txn.application_args[1] != NULL_OPTION, 
           Seq([App.globalPut(Concat(OPTION_PREFIX, Txn.application_args[1]), ZERO)]),
           Return(Int(1))
        ),
        If(Txn.application_args[2] != NULL_OPTION, 
          Seq([App.globalPut(Concat(OPTION_PREFIX, Txn.application_args[2]), ZERO)]),
           Return(Int(1))
        ),
        If(Txn.application_args[3] != NULL_OPTION, 
          Seq([App.globalPut(Concat(OPTION_PREFIX, Txn.application_args[3]), ZERO)]),
           Return(Int(1))
        ),
        If(Txn.application_args[4] != NULL_OPTION, 
          Seq([App.globalPut(Concat(OPTION_PREFIX, Txn.application_args[4]), ZERO)]),
           Return(Int(1))
        ),
        If(Txn.application_args[5] != NULL_OPTION, 
          Seq([App.globalPut(Concat(OPTION_PREFIX, Txn.application_args[5]), ZERO)]),
           Return(Int(1))
        ), 
        Return(Int(1))
    ])
    
    
    on_creation = Seq([    
        App.globalPut(Bytes("Creator"), Txn.sender()),    
        App.globalPut(Bytes("Name"), Txn.application_args[0]),
        App.globalPut(Bytes("asset_id"), Btoi(Txn.application_args[6])),  # should be Int 
        App.globalPut(Bytes("asset_coefficient"), Btoi(Txn.application_args[7])), 
        on_add_options,   # record the options 
        Return(Int(1))
    ])    
    
        
    program = Cond(    
            [Txn.application_id() == Int(0), on_creation],    
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))], 
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],    
            [Txn.on_completion() == OnComplete.OptIn, on_optin],
            [Txn.application_args[0] == Bytes("vote"), on_vote],
            [Txn.application_args[0] == Bytes("add_options"), on_add_options]
    )    
    return program    
    
    
def clear_state_program():     
    program = Return(Int(1))
    return program    


if __name__ == "__main__":
    teal_dir = "teal/"

    if len(sys.argv) < 2: 
        approval_filename = teal_dir + "quadratic_voting_approval.teal"
        clear_state_filename = teal_dir + "quadratic_voting_clear_state.teal"
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






