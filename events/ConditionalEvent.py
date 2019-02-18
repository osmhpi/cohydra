import ns.core
from aexpr import aexpr


class ConditionalEvent(object):

    def __init__(self, condition, globals, locals):
        self.condition = condition
        self.globals = globals
        self.locals = locals
        self.lambda_expression = None

    def execute(self, lambda_expression):
        self.lambda_expression = lambda_expression
        ns.core.Simulator.Schedule(ns.core.Seconds(0), self.run)

    def run(self):
        if self.lambda_expression is not None:
            aexpr(self.condition, self.globals, self.locals).on_change(self.lambda_expression)
