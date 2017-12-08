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