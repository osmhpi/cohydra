import ns.core


class TimedEvent(object):

    def __init__(self, seconds):
        self.seconds = seconds
        self.lambda_expression = None

    def execute(self, lambda_expression):
        self.lambda_expression = lambda_expression
        ns.core.Simulator.Schedule(ns.core.Seconds(self.seconds), self.run)

    def run(self):
        if self.lambda_expression is not None:
            self.lambda_expression()
