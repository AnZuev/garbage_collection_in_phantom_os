from processes.ds import *


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