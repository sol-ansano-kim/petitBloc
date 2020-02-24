import re
import subprocess


ReLineEnding = re.compile("\n|\r\n")


class SubprocessWorker(object):
    def __init__(self, cmd):
        self.__command = cmd
        self.__outputs = []
        self.__errors = []
        self.__p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def command(self):
        return self.__command

    def isRunning(self):
        return self.__p.poll() is None

    def result(self):
        log = self.__p.communicate()
        self.__outputs = filter(lambda x: x, ReLineEnding.split(log[0]))
        self.__errors = filter(lambda x: x, ReLineEnding.split(log[1]))

        return self.__p.returncode == 0

    def outputs(self):
        return self.__outputs

    def errors(self):
        return self.__errors
