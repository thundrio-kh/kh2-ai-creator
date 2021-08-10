# No function support

# manual push pops
# Calling a function with X methods
# some basic comparisons 
# quit 
# constants support

import sys, json

#filename = "lk_get_craw.bdx"
filename = sys.argv[1]

bdx = open(filename).read().split("\n")
name = filename.split(".")[0]

PRINT_ASSEMBLY = True

DEBUG_INSTRUCTIONS = False

def doConst(management, line_syntax):
    try:
        name = line_syntax[1]
        value = int(line_syntax[2])
    except:
        print("ParseError error converting {} to int".format(line_syntax))
        value = int(line_syntax[1])
    if name in management["constants"]:
        raise Exception("ConstantError: Constant already defined {}".format(name))
    management["constants"][name] = value

def doPush(management, line_syntax=None, value=None):
    if not value:
        value = int(line_syntax[1])
    management["instructions"].append("pushImm {}".format(value))

def doPop(management, line_syntax=None, value=None):
    raise Exception("Not Implemented")

def doCall(management, line_syntax):
    ls = ''.join(line_syntax[1:]).split("(")
    trap_name = ls[0]
    arguments = [a for a in ls[1].split(")")[0].split(",") if len(a)]
    for arg in arguments:
        argument = arg
        if arg in management["constants"]:
            argument = management["constants"][arg]
        doPush(management, value=argument)
    management["instructions"].append(trap_name)

def doQuit(management, line_syntax):
    management["instructions"].append("ret")

def doIf(management, line_syntax):
    raise Exception("Not Implemented")

def doLabel(management, line_syntax):
    label_name = ' '.join(line_syntax[1:])
    management["end_labels"].append(label_name)
    
def assembleBDX(management):
    # long term I don't want to use management here, just the raw instructions
    instructions = json.load(open("instructions.json"))
    traps = json.load(open("traps.json"))
    instructions = {
        "pushImm": [0x80, 0],
        "ret": [0x89, 0]
    }
    traps = json.load(open("traps.json"))

    hexdump = bytearray(name, "utf-8")
    while len(hexdump) < 16:
        hexdump.append(0) # delimiter

    import struct

    hexdump += bytearray(struct.pack("<i", management["sizes"]["workSize"]))
    hexdump += bytearray(struct.pack("<i", management["sizes"]["stackSize"]))
    hexdump += bytearray(struct.pack("<i", management["sizes"]["termSize"]))

    # Just a default triggers section, will need to be real for more advanced stuff
    hexdump += bytearray([2, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    for instruction in management["instructions"]:
        if instruction.startswith("trap"):
            trapbytes = bytearray([])
            trapbytes += bytearray([0xa,0])
            trap = traps[instruction]

            trapbytes += bytearray(int(trap["tableIdx"]))
            trapbytes += bytearray(struct.pack("<h", int(trap["funcIdx"])))

            if DEBUG_INSTRUCTIONS:
                print("{} = {}".format(instruction, ' '.join([hex(i)[2:].zfill(2) for i in trapbytes])))
            hexdump += trapbytes
        else:
            split = instruction.split(" ")
            instr = split[0]
            if instr not in instructions:
                raise Exception("Instruction not found: {}".format(instr))
            instrbytes = bytearray(instructions[instr])
            if instr == "pushImm":
                instrbytes = bytearray(struct.pack("<i", int(split[1])))
            if DEBUG_INSTRUCTIONS:
                print("{} = {}".format(instruction, ' '.join([hex(i)[2:].zfill(2) for i in instrbytes])))
            hexdump += instrbytes

    # for l in range(len(management["end_labels"])):
    #     label = management["end_labels"][l]
    #     hexdump += bytearray(name, "utf-8")
    #     hexdump += bytearray([0,0]) 

    # hacking the end together
    hexdump += bytearray([106, 117, 109, 112, 32, 115, 116, 97, 114, 116, 0, 0, 106, 117, 109, 112, 32, 101, 110, 100, 0, 0])

    # str([i for i in hexdump])
    # for i in range(len(correct)):
    #     x = correct[i]
    #     y = hexdump[i] if i < len(hexdump) else '_'
    #     print("{} {}".format(x, y))
    return hexdump


commands = {
    "constant": doConst,
    "push": doPush,
    "pop": doPop,
    "call": doCall,
    "quit": doQuit,
    "If": doIf,
    "label": doLabel
}

management = {
    "sizes": {
        "workSize": 0,
        "stackSize": 512,
        "termSize": 512
    },
    "constants": {},
    "instructions": [],
    "end_labels": [
    ]
}

for line in bdx:
    # Allow python style comments
    if len(line.strip()) == 0:
        continue
    elif line.startswith("#"):
        continue
    elif '#' in line:
        line = line.split("#")[0]

    if line.startswith("workSize:"):
        management["sizes"]["workSize"] = int(line.split(" ")[1])
        continue
    elif line.startswith("stackSize:"):
        management["sizes"]["stackSize"] = int(line.split(" ")[1])
        continue
    elif line.startswith("termSize:"):
        management["sizes"]["termSize"] = int(line.split(" ")[1])
        continue

    line_syntax = line.strip().split(" ")
    command = line_syntax[0]
    if command not in commands:
        raise Exception("SyntaxError: Command not found: {}".format(command))
    commands[command](management, line_syntax)

if management["instructions"][-1] != "ret":
    management["instructions"].append("ret")


if PRINT_ASSEMBLY:
    print("\n".join(["{}: {}".format(k,v) for k,v in management["sizes"].items()]))
    print("\n")
    print("\n".join(management["instructions"]))
    print("\n")
    print("\n".join(management["end_labels"]))


# Now create the BDX off the assembly
open("output.bdx", "wb").write(assembleBDX(management))