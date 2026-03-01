'''
hw7-q1-DirectMapped.py

    Tyler Schill

    Created February 2026

** Based loosely on Python reading file program
   by Tucker L. Ward **
'''

import sys


### Input Validation ###

# Globals
g_cache_type = ''
g_verbose = ''
g_filename = ''

def validate_input(num_args):
    # we want to use global variable
    global g_filename

    # helper function
    def set_cache_type(cache_arg):
        # need to put this here as opposed
        # to outside the function because
        # doesn't transfer from outer function
        # into this one
        global g_cache_type

        if cache_arg == 'dm':
            g_cache_type = 'direct-mapped'
        elif cache_arg == '2sa':
            g_cache_type = 'two-way-set-associative'
        elif cache_arg == '4sa':
            g_cache_type = 'four-way-set-associative'
        elif cache_arg == 'fa':
            g_cache_type = 'fully-associative'
        else:
            print("ERROR: not a valid cache type")
            print("USAGE: python hw7-q1-DirectMapped.py {dm/2sa/4sa/fa} {v(erbose)} {filename}")
            exit(-1)

    # helper function
    def set_verbose(verbose_arg):
        global g_verbose

        if verbose_arg == 'v':
            g_verbose = 'yes'
        else:
            g_verbose = 'no'

    if num_args == 4:
        set_cache_type(sys.argv[1])
    
        set_verbose(sys.argv[2])

        g_filename = sys.argv[3]

    elif num_args == 3:
        set_cache_type(sys.argv[1])
    
        set_verbose(sys.argv[2])

        g_filename = sys.argv[2]

    elif num_args > 4:
        print("ERROR: too many arguments")
        print("USAGE: python hw7-q1-DirectMapped.py {dm/2sa/4sa/fa} {v(erbose)} {filename}")
        exit(-1)
    else:
        print("ERROR: not enough arguments")
        print("USAGE: python hw7-q1-DirectMapped.py {v(erbose)} {filename}")
        exit(-1)


### Read the file ###

# Globals
g_args = []

def read_file():
    global g_args

    file = open(g_filename, "r")

    if not file:
        print(f'ERROR: could not open file {filename}')
        exit(-1)

    line = file.readline()
    while line:
        # remove leading/trailing white space
        stripped_line = line.strip()

        # split components by space
        line_args = stripped_line.split(" ")
        
        # global args is 2D array with each index
        # being the arguments from one line of the file
        g_args.append(line_args)

        line = file.readline()

    file.close()


### Logistics ###

def print_logistics():

    print(g_filename)

    if g_verbose == 'yes':
        print("Verbose")
    
    print(f"Tagmask: {g_tagmask}")
    print(f"Setmask: {g_setmask}")
    print(f"Mode: {g_cache_type}")

    print(f"64 blocks, 16 bytes in a block; {len(g_cache)} sets, {len(g_cache[0])} lines per set")
  

### Verbose Output ###

# keeps track of how many addresses we've seen
g_iteration = 1

def print_verbose_output(data_instruction, address, tag, set_, lines, hit_miss, empty_evict, line):
    # what we're looking for
    print("-----------------------------")
    print(f"{data_instruction} {g_iteration}: ", end="")
    print(f"addr {hex(address)}; ", end="")
    print(f"looking for tag {hex(tag)} ", end="")
    print(f"in set {hex(set_)}.")

    # state of the set
    print(f"\nState of set {hex(set_)}:")
    
    for i in range(0, len(lines)):
        print(f"line {i} V={lines[i][0]} Tag={hex(lines[i][1])} Last_Touch={lines[i][2]}")

    # action we took
    if hit_miss == 'hit':
        print(f"Found it in line {line}. Hit! Updating last_touch to {g_iteration}")
    else:
        if empty_evict == 'empty':
            print(f"Miss! Found empty line {line}; adding block there; setting last touch to {g_iteration}")
        else:
            print(f"Miss! Evicting line {line}; adding block there; setting last touch to {g_iteration}")


### Cache Implementation ###

# Globals
g_cache = []
g_tagmask = 0x0
g_setmask = 0x0
g_hits = 0
g_misses = 0

def setup_cache():
    global g_cache
    global g_tagmask
    global g_setmask

    set_ = []
    # Structure:
    # (valid, tag, last_touch)
    data = [0, 0, 0]

    if g_cache_type == 'direct-mapped':
        # setup masks
        g_tagmask = hex(0xffffffc0)
        g_setmask = hex(0x0000003f)

        for i in range(0, 64):
            # Structure:
            # (valid, tag, last_touch)
            set_.append(data)
            g_cache.append(set_)
            set_ = []

    elif g_cache_type == 'two-way-set-associative':
        g_tagmask = hex(0xffffffe0)
        g_setmask = hex(0x0000001f)

        for i in range(0, 32):
            set_ = []
            for j in range(0, 2):
                set_.append(data)
            g_cache.append(set_)

    elif g_cache_type == 'four-way-set-associative':
        g_tagmask = hex(0xffffff00)
        g_setmask = hex(0x000000f0)

        for i in range(0, 16):
            set_ = []
            for j in range(0, 4):
                set_.append(data)
            g_cache.append(set_)

    else:
        g_tagmask = hex(0xfffffff0)
        g_setmask = hex(0x00000000)

        for i in range(0, 64):
            set_.append(data)
        g_cache.append(set_)

    #print(g_cache)

def run_cache():
    global g_args
    global g_iteration
    global g_tagmask
    global g_setmask
    global g_hits
    global g_misses

    #print(f"Args len: {len(g_args)}")

    # convert masks to int so we can do bitwise ops
    g_tagmask = int(g_tagmask, 16)
    g_setmask = int(g_setmask, 16)

    for i in range(0, len(g_args)):
        # find out where to look in our cache
        data_instruction = g_args[i][0]
        address = g_args[i][1]

        # convert address to int so we can do bitwise ops
        address = int(address, 16)

        # find tag and set
        tag = address & g_tagmask
        set_ = address & g_setmask

        # look at state of this part of cache
        lines = g_cache[set_]
        
        # while we iterate, take note of any open lines
        open_lines = []

        # keep track of index of oldest line (we will evict this onefirst
        oldest_touch = 0
        oldest_line_index = 0

        for i in range(0, len(lines)):
            # look for a hit
            #print(f"DEBUG#######: {lines[i][0]}")
            #print(f"DEBUG#######: {lines[i][2]}")
            if lines[i][0] == 1 and lines[i][1] == tag:
                # Hit!
                g_hits += 1
                hit_miss = 'hit'
                empty_evict = ''
                line = i

                # update cache accordingly
                lines[i][2] = g_iteration
                
                # print if verbose output is set
                if g_verbose == 'yes':
                    print_verbose_output(data_instruction, address, tag, set_, lines, hit_miss, empty_evict, line)

            elif lines[i][0] == 0:
                open_lines.append(i)
                print(f"DEBUG#####: {oldest_touch}")
                if lines[i][2] < oldest_touch:
                    oldest_line_index = i

        # Miss!
        g_misses += 1
        hit_miss = 'miss'

        if len(open_lines) > 0:
            empty_evict = 'empty'
            line = open_lines[0]

            print_verbose_output(data_instruction, address, tag, set_, lines, hit_miss, empty_evict, line)

            # update cache accordingly
            g_cache[set_][line] = [1, tag, g_iteration]

        else:
            empty_evict = 'evict'
            line = oldest_line_index

            print_verbose_output(data_instruction, address, tag, set_, lines, hit_miss, empty_evict, line)

            # update cache accordingly
            g_cache[set_][line] = [1, tag, g_iteration]

        # we have just gone through another iteration
        g_iteration += 1


### Final Stats ###
def print_final_stats():
    print("-----------------------------")
    print("-----------------------------")
    print(f"\nHits: {g_hits}")
    print(f"Misses: {g_misses}")
    print(f"Addresses: {g_iteration - 1}")


### Main ###
def main():
    validate_input(len(sys.argv))
    read_file()
    setup_cache()
    print_logistics()
    run_cache()
    print_final_stats()

if __name__ == "__main__":
    main()
