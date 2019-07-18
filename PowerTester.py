#!/usr/bin/env python3
from subprocess import Popen, PIPE
from argparse   import ArgumentParser
import datetime
from time       import sleep
import time

from AgilentScope import AgilentScope
from LecroyScope import LecroyScope

class PowerTester(object):
    def __init__(self):
        self.startTime = datetime.datetime.now()
        self.timeString = self.startTime.strftime("%Y%m%d_%H%M%S")
        self.parseArgument()
        self.openLogFile('logs/')
        self.openDataFiles('data/')
        self.openProcess('runner.py')
        
        if self.scopeName == "lecroy":
           self.scope = LecroyScope()
           print 'Setup completed.'
        else:
            self.scope = AgilentScope()
            # if self.scopeName != "agilent":
                # print("Unrecognized scope name, use agilent as default")
                
        self.writeScopeInfo()
        
    def __del__(self):
        if hasattr(self, 'logFile'):
            self.logFile.close()
        if hasattr(self, 'dataFiles'):
            for f in self.dataFiles:
                f.close()
        if hasattr(self, 'result'):
            self.result.close()
        if hasattr(self, 'process') and self.process.poll() == None:
            self.process.terminate()
        timeUsed = datetime.datetime.now() - self.startTime
        print("Time used: ", timeUsed)

    def parseArgument(self):
        parser = ArgumentParser(description = "adiSiometric power measurement")
        parser.add_argument("--dataFileName", default="powerData", type=str, help="file name for data")
        parser.add_argument("--nTraces",      default=10,          type=int, help="number of traces to collect")
        parser.add_argument("--channels", default=[1], nargs='+', type=int, help="channels with waveform")
        parser.add_argument("--scopeName", default="lecroy", type=str, help="set the scope, agilent or lecroy")
        parser.add_argument("--command", default="r", type=str, help="the command sent to tokenTest")
        parser.add_argument("--ciphertextNumber", default=0, type=int,\
                            help="selection of ciphertext if command is 'd'")
        # ciphertext & plaintext file name pass to process
        parser.add_argument("--ciphertextFileName", default="ciphertext", type=str,\
                            help="file name for ciphertext")
        parser.add_argument("--plaintextFileName",  default="plaintext",  type=str,\
                            help="file name for plaintext")
        parser.add_argument("--messageFileName", default="message", type=str,\
                            help="file name for message")
        parser.add_argument("--signatureFileName",  default="signature",  type=str,\
                            help="file name for signature")
        args = parser.parse_args()
        self.dataFileName = args.dataFileName
        self.nTraces = args.nTraces
        self.channels = args.channels
        self.ciphertextFileName = args.ciphertextFileName
        self.plaintextFileName = args.plaintextFileName
        self.messageFileName = args.messageFileName
        self.signatureFileName = args.signatureFileName
        self.scopeName = args.scopeName
        self.command = args.command
        self.ciphertextNumber = args.ciphertextNumber
        
    def openLogFile(self, logDir = "/home/chao/adiSiometric/log"):
        logFileName = logDir + '/' + "log_" + datetime.datetime.today().strftime('%m-%d-%y')
        self.logFile = open(logFileName, 'w')

    def openDataFiles(self, dataDir = "/home/chao/adiSiometric/data"):
        self.result = open("%s/result-%s.txt" % (dataDir, datetime.datetime.today().strftime('%m-%d-%y')), 'w')
        self.dataFiles = []
        for i in self.channels:
            dataFileFullName = dataDir + '/' + self.dataFileName + str(i) + '_' +\
                               str(self.nTraces ) + '_' + datetime.datetime.today().strftime('%m-%d-%y')
            dataFile = open(dataFileFullName, "wb")
            self.dataFiles.append(dataFile)

    def writeScopeInfo(self):
        for i in range(len(self.channels)):
            info = self.scope.getSampleRate() + self.scope.getChannelInfo(self.channels[i]) +\
                   self.scope.getTimeInfo()
            self.dataFiles[i].write(info.encode())

    def openProcess(self, command = "/home/chao/adiSiometric/build/tokenTest"):
        commands = ['python', command]
        self.process = Popen(commands, stdin = PIPE, stdout = PIPE)
        time.sleep(5)

    def wait_until_ready(self):
        while True:
            line = self.process.stdout.readline().strip()
            if 'Waiting' in line:
                return True

    def get_result(self):
        while True:
            line = self.process.stdout.readline().strip()
            if 'ERROR' in line:
                print line
                exit(1)
            return line

    def _check_result(self, result):
        return len("5e 13 4a 7b 50 a7 23 32 55 ec 8b 7d ac 27 b1 62") == len(result)

    def doit(self):
        for i in range(self.nTraces):
            self.scope.digitize()
            # delay command for the first trace
            if i == 0 or i == 1:
                sleep(0.5)
            sleep(0.1)
            print "Trace: ", i+1
            self.wait_until_ready()
            # start encryption
            self.process.stdin.write('\n')
            # collect ciphertext
            result = self.get_result()
            success = self._check_result(result)
            print 'waiting scope to be finished'
            if (self.scope.waitUntilCompleted()):
                # skip the trace if there is an error
                if success == False: continue
                # collect power trace
                waves = self.scope.readData(self.channels)
                # write data to files
                for i,c in enumerate(self.channels):
                    self.dataFiles[i].write(waves[i])
                self.result.write(result + '\n')
                self.result.flush()
                continue
            else:
                print "Cannot wait for the scope to be completed."
            # break

if __name__ == "__main__":
    powerTester = PowerTester()
    powerTester.doit()
