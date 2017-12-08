from processes.ds import GC, MethodInfo


def init_methods_table(tree):
    # key - method
    # value - dict with key - param_name and value - pass_forward/doesn't_change/not_sure)
    methods_table = dict()
    for t in tree.types:
        if str(t) == 'ClassDeclaration':
            class_name = t.name
            for method in t.methods:
                methods_table[".".join([class_name, method.name])] = MethodInfo(".".join([class_name, method.name]), list(map(lambda x: x.name, method.parameters)))
    return methods_table


def read_program(filename):
    f = open(filename, 'r')
    program = f.read()
    f.close()
    return program
