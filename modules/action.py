from .interface import Interface

class Action:

    def default_precond_func():
        return True

    def default_action_func(caller_dict: dict):
        return caller_dict
    
    def __init__(self, action_name = "Mysterious Action", precond_func = default_precond_func, action_func = default_action_func):
        self.action_name = action_name # Used to identify the action.
        self.precond_func = precond_func # Stores the function used to determine whether to run the action function or not.
        self.action_func = action_func # Stores the function that is referenced whenever the action is triggered.
        self.interface = Interface()

    def get_name(self):
        return self.action_name
    
    # Returns False if the action did not run, else return True.
    def run_action(self):
        # Handle block outputs in the preconditions function.
        if self.precond_func() == True:
            # Handle data modifications via the action function.
            self.action_func()
            return True
        return False
