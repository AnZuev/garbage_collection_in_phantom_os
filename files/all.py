from enum import Enum


class GC(Enum):
    pass_forward = -1
    does_not_change = 1
    not_sure = 0


class Scope:
    def __init__(self, parent_scope = None):
        self.parent_scope = parent_scope
        self.local_vars = dict()
        self.tracked_vars = dict()
        self.vars_to_delete = set()

    def get_parent(self):
        return self.parent_scope

    def is_being_tracked(self, var):
        tracked_vars = self.tracked_vars
        scope = self
        while tracked_vars.get(var, None) is not None:
            if scope.get_parent():
                scope = scope.get_parent()
            else:
                return False
        return tracked_vars.get(var)

    def add_local_var(self, var):
        self.local_vars[var] = self.local_vars.get(var, 0) + 1

    def make_trackable(self, var):
        # value is just a placeholder,
        # the real purpose to store the key
        self.tracked_vars[var] = 1

    # method to make a decision what variable is safe to delete
    # inside this scope
    def decide(self):
        pass


class MethodInfo:
    def __init__(self, title, param_names):
        self.title = title
        self.param_names = param_names
        self.param_table = dict()

        for name in param_names:
            self.param_table[name] = GC.does_not_change

    def change_gc_state_of_the_param(self, param_name, new_gc_state):
        if new_gc_state not in GC:
            raise Exception("Couldn't assign", new_gc_state, "type to param", param_name)
        param = self.param_table.get(param_name, None)
        if param is not None:
            self.param_table[param_name] = new_gc_state
        else:
            print("There is no param", param_name, "in method", self.title)
            

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

def process_class(class_obj):
    # first we need to init scope
    # scope for class consists only of fields
    scope = Scope()

    for field in class_obj.fields:
        for decl in field.declarators:
            scope.add_local_var(decl.name)
    return scope

    for method in class_obj.methods:
        process_method(method, class_obj, scope)


def process_method(method, class_object, class_scope):
    scope = Scope(class_scope)
    for param in method.parameters:
        scope.make_trackable(param.name)

    for command in method.body:
        process_command(command, scope)


# command
def process_command(command, scope):
    pass


# always return False because doesn't change gc of the object
def process_literal_declaration(variable, scope):
    return False


# return True if member_reference is interesting_object
# otherwise False
def process_member_reference(member_reference, scope):
    return scope.is_being_tracked(member_reference.member) is not None


# processes classCreator
def process_class_creator(obj, scope):
    for arg in obj.arguments:
        process_expression(arg, scope)


def process_expression(expression, scope):
    expression_type = str(expression)

    if expression_type == "BinaryOperation":
        process_expression(expression.loperand, scope)
        process_expression(expression.roperand, scope)
    else:
        handler = basicHandlers.get(expression_type, None)
        if handler is not None:
            handler(expression, scope)
        else:
            print("Can't process expr of type ", expression_type)


def process_variable_declarator(obj, scope):
    handler = basicHandlers.get(str(obj.initializer), None)
    if handler:
        if handler(obj.initializer, scope):
            scope.add_local_var(obj.name)
            scope.make_trackable(obj.name)
        else:
            scope.add_local_var(obj.name)
    else:
        print("Can't process", str(obj))


def process_local_variable_declaration(declaration, scope):
    variables = declaration.children[3]
    for var in variables:
        process_variable_declarator(var, scope)


basicHandlers = dict()

basicHandlers['LocalVariableDeclaration'] = process_local_variable_declaration
basicHandlers['Literal'] = process_literal_declaration
basicHandlers['MemberReference'] = process_member_reference
basicHandlers['ClassCreator'] = process_class_creator