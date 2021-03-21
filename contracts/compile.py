import sys 
import QuadraticVoting
import Queue


def compile(approval_filename='approval.teal', clear_state_filename='clear_state.teal'):

    # pyteal to teal 
    with open(approval_filename, 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open(clear_state_filename, 'w') as f:
        compiled = compileTeal(clear_state_program(), Mode.Application)
        f.write(compiled)

    # teal to bytecode 
    stdout, stderr = execute(["goal", "clerk", "compile", "-o", approval_filename+'.tok', approval_filename])
    if stderr != "":
        print(stderr)
        raise
    elif len(stdout) < 59:
        print("error in compile teal")
        raise

    stdout, stderr = execute(["goal", "clerk", "compile", "-o", clear_state_filename+'.tok', clear_state_filename])
    if stderr != "":
        print(stderr)
        raise
    elif len(stdout) < 59:
        print("error in compile teal")
        raise

    with open(approval_filename+'.tok', 'rb') as f:
        approval_bytes = f.read()

    with open(clear_state_filename+'.tok', 'rb') as f: 
        clear_state_bytes = f.read() 
        
    return approval_bytes, clear_state_bytes


if __name__ == "__main__":
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    hello(a, b)

