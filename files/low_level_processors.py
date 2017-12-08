from processes.ds import *
from processes.high_level_processors import *


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