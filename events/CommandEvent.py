import ns.core
import subprocess
import threading


class CommandEvent(object):

    def __init__(self, seconds, command):
        self.seconds = seconds
        self.command = command
        self.returncode = 0
        self.lambda_expression = None

    def check_if(self, command):
        self.command = command
        return self

    def returns(self, returncode):
        self.returncode = returncode
        return self

    def then_execute(self, lambda_expression):
        self.lambda_expression = lambda_expression
        ns.core.Simulator.Schedule(ns.core.Seconds(0), self.run)

    def run(self):
        if self.lambda_expression is not None and self.command is not None:
            if self.seconds < 0:
                self.execute_command_and_check()
            else:
                def runit():
                    if self.execute_command_and_check() is not True:
                        self.timer = threading.Timer(self.seconds, runit).start()
                runit()

    def execute_command_and_check(self):
        returncode = subprocess.call(self.command, shell=True)
        if returncode == self.returncode:
            self.lambda_expression()
            return True
        return False
