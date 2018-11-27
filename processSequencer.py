import os
import sys
import subprocess
import signal
import time
import json


class Connector(object):
    def __init__(self):
        self.process = ""
        self.port = ""


comboFD = 0
dbg = False
sequencedProcessListJson = []
dataReadyList = []
components = []
connections = []
processes = []
sequencedProcessNames = []


def init_processes():
    tempDict = {}
    tempDict['name'] = "waveshaperb_1"
    tempDict['inputs'] = ["input"]
    tempDict['outputs'] = ["output"]
    processes.append(tempDict)

    tempDict = {}
    tempDict['name'] = "filter3bb_0"
    tempDict['inputs'] = ["input"]
    tempDict['outputs'] = ["low","mid","high"]
    processes.append(tempDict)

    tempDict = {}
    tempDict['name'] = "mixerb_1"
    tempDict['inputs'] = ["input1","input2","input3"]
    tempDict['outputs'] = ["output"]
    processes.append(tempDict)

    tempDict = {}
    tempDict['name'] = "filter3bb_1"
    tempDict['inputs'] = ["input"]
    tempDict['outputs'] = ["low","mid","high"]
    processes.append(tempDict)

    tempDict = {}
    tempDict['name'] = "mixerb_0"
    tempDict['inputs'] = ["input1","input2","input3"]
    tempDict['outputs'] = ["output"]
    processes.append(tempDict)

    tempDict = {}
    tempDict['name'] = "waveshaperb_0"
    tempDict['inputs'] = ["input"]
    tempDict['outputs'] = ["output"]
    processes.append(tempDict)

def init_connections():


    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_0"
    tempDict['srcPort'] = "low"
    tempDict['destProcess'] = "mixerb_1"
    tempDict['destPort'] = "input1"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_0"
    tempDict['srcPort'] = "mid"
    tempDict['destProcess'] = "mixerb_1"
    tempDict['destPort'] = "input2"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_0"
    tempDict['srcPort'] = "high"
    tempDict['destProcess'] = "mixerb_1"
    tempDict['destPort'] = "input3"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "mixerb_1"
    tempDict['srcPort'] = "output"
    tempDict['destProcess'] = "waveshaperb_1"
    tempDict['destPort'] = "input"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_1"
    tempDict['srcPort'] = "low"
    tempDict['destProcess'] = "mixerb_0"
    tempDict['destPort'] = "input1"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_1"
    tempDict['srcPort'] = "mid"
    tempDict['destProcess'] = "mixerb_0"
    tempDict['destPort'] = "input2"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "filter3bb_1"
    tempDict['srcPort'] = "high"
    tempDict['destProcess'] = "mixerb_0"
    tempDict['destPort'] = "input3"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "mixerb_0"
    tempDict['srcPort'] = "output"
    tempDict['destProcess'] = "waveshaperb_0"
    tempDict['destPort'] = "input"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "waveshaperb_1"
    tempDict['srcPort'] = "output"
    tempDict['destProcess'] = "system"
    tempDict['destPort'] = "playback_1"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "system"
    tempDict['srcPort'] = "capture_1"
    tempDict['destProcess'] = "filter3bb_1"
    tempDict['destPort'] = "input"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "waveshaperb_0"
    tempDict['srcPort'] = "output"
    tempDict['destProcess'] = "filter3bb_0"
    tempDict['destPort'] = "input"
    connections.append(tempDict)

    tempDict = {}
    tempDict['srcProcess'] = "system"
    tempDict['srcPort'] = "capture_2"
    tempDict['destProcess'] = "system"
    tempDict['destPort'] = "playback_2"
    connections.append(tempDict)





def getTargetProcessIndex(processName):
    if dbg: print "entering: ComboDataInt::getTargetProcessIndex"
    targetProcessIndex = 0
    # get index for target process
    for processIndex in range(0, len(processes)):
        if processName == processes[processIndex]['name']:
            targetProcessIndex = processIndex
            break
        if processIndex == len(processes) - 1:
            targetProcessIndex = -1
    if dbg: print "exiting: ComboDataInt::getTargetProcessIndex"
    return targetProcessIndex

def getConnectionDestinationIndex(destinationProcessName):
    if dbg: print "entering: ComboDataInt::getConnectionDestinationIndex"
    targetConnectionIndex = 0
    ## get index for target process
    for connectionIndex in range(0,len(connections)):
        if destinationProcessName == connections[connectionIndex]["destProcess"]:
            targetConnectionIndex = connectionIndex
            break
        if connectionIndex == len(connections) - 1:    # #end of connection array reach, but no match found
            targetConnectionIndex = -1
    if dbg: print "exiting: ComboDataInt::getConnectionDestinationIndex"
    return targetConnectionIndex


def getProcessInputs(process_name):
    if dbg: print "entering: ComboDataInt::getProcessInputs"
    inputs = []
    target_index = getTargetProcessIndex(process_name)

    for input_index in range(0, len(processes[target_index]["inputs"])):
        inputs.append(processes[target_index]["inputs"][input_index]);

    if dbg:
        for i in range(0,len(inputs)):
            print("inputs[%d]: %s" % (i,inputs[i]))


    if dbg: print "exiting: ComboDataInt::getProcessInputs"
    return inputs

def getProcessOutputs(process_name):
    if dbg: print "entering: ComboDataInt::getProcessOutputs"
    outputs = []
    target_index = getTargetProcessIndex(process_name)

    for output_index in range(0, len(processes[target_index]["outputs"])):
        outputs.append(processes[target_index]["outputs"][output_index])
    if dbg:
        for i in range(0,len(outputs)):
             print("outputs[%d]: %s" % (i,outputs[i]))

    if dbg: print "exiting: ComboDataInt::getProcessOutputs"
    return outputs

def fillUnsequencedProcessList():
    if dbg: print "entering: ComboDataInt::fillUnsequencedProcessList"

    init_processes()

    if dbg: print "exiting: ComboDataInt::fillUnsequencedProcessList"


def areDataBuffersReadyForProcessInputs(processName):
    # since data buffers are fed by process outputs, the dataReadyList contains the output process:port names

    # get process outputs that feed data buffers using process inputs and connection list.
    # Start at known process inputs and use connection list to work backwards toward outputs of previous processes.

    if dbg: print "entering: ComboDataInt::areDataBuffersReadyForProcessInputs"
    allProcessOutputsContainedInConnectionList = True
    dataReadyMatches = [True,True,True,True,True,True,True,True,True,True]
    inputs = getProcessInputs(processName)
    procOutputs = []

    for inputIndex in range(0,len(inputs)):
        for connIndex in range(0,len(connections)):
            srcProcess = connections[connIndex]["srcProcess"]
            srcPort = connections[connIndex]["srcPort"]
            destProcess = connections[connIndex]["destProcess"]
            destPort = connections[connIndex]["destPort"]

            # if connection dest process:port matches process input, put src process:port in procOutputs
            if(processName == destProcess and inputs[inputIndex] == destPort):
                tempConn = Connector()
                tempConn.process = srcProcess
                tempConn.port = srcPort
                procOutputs.append(tempConn)

    if dbg:
        for output in procOutputs:
            print output.process + ":" + output.port
    # are output process:ports that feed relevant data buffers in dataReadyList
    for outputIndex in range(0,len(procOutputs)):
        for dataReadyIndex in range(0,len(dataReadyList)):
            if(procOutputs[outputIndex].process == dataReadyList[dataReadyIndex].process) and \
                            (procOutputs[outputIndex].port == dataReadyList[dataReadyIndex].port):
                break;
            if(dataReadyIndex == len(dataReadyList) - 1): #end of connection array reach, but no match found
                dataReadyMatches[dataReadyIndex] = False

    for dataReadyIndex in range(0,10):
        allProcessOutputsContainedInConnectionList &= dataReadyMatches[dataReadyIndex]

    if dbg: print "exiting: ComboDataInt::areDataBuffersReadyForProcessInputs"

    return allProcessOutputsContainedInConnectionList

def isUnsequencedProcessListEmpty():
    if dbg: print "entering: ComboDataInt::isUnsequencedProcessListEmpty"

    if(len(processes) == 0): isListEmpty = True
    else: isListEmpty = False
    if dbg:
        for i in range(0,len(processes)):
            print processes[i]["name"]

    if dbg: print("isListEmpty: %s" % isListEmpty)
    if dbg: print "exiting: ComboDataInt::isUnsequencedProcessListEmpty"

    return isListEmpty;

def isOutputInDataReadyList(output):
    if dbg: print "***************entering: isOutputInDataReadyList***************"
    inList = False
    #print("output: %s:%s" % (output.process,output.port))
    for listedOutput in dataReadyList:
        #outputString = output.process + ":" + output.port
        if dbg: print listedOutput.process + ":" + listedOutput.port #outputString
        if output.process == listedOutput.process and output.port == listedOutput.port:
            inList = True
            break
    return inList

def getFirstProcess():
    if dbg: print "***************entering: ComboDataInt::getFirstProcess***************"
    srcProcess = "system"
    srcPort = "capture_1"
    foundNextProcess = False
    firstProcess = "none"

    for  connIndex in range(0,len(connections)):
        if(srcProcess == connections[connIndex]["srcProcess"] and \
                        srcPort == connections[connIndex]["srcPort"]):
            tempConn = Connector()
            tempConn.process = connections[connIndex]["srcProcess"]
            tempConn.port = connections[connIndex]["srcPort"]
            if(foundNextProcess == False):
                firstProcess = connections[connIndex]["destProcess"]
                foundNextProcess = True

    if dbg:
        for  i in range(0,len(dataReadyList)):
            print("dataReadyList[%d]: %s:%s" % (i,dataReadyList[i].process,dataReadyList[i].port))

    if dbg: print "exiting: ComboDataInt::getFirstProcess"
    return firstProcess;

def getNextProcess(srcProcess):
    foundNextProcess = False

    ## loop through processes and get the first one that has inputs ready with data

    for connIndex in range(0, len(connections)):
        if(srcProcess == connections[connIndex]["srcProcess"]):
            tempConn = Connector()
            tempConn.process = connections[connIndex]["srcProcess"]
            tempConn.port = connections[connIndex]["srcPort"]
            if(foundNextProcess == False):
                nextProcess = connections[connIndex]["destProcess"]
                foundNextProcess = True

    if dbg: print "exiting: ComboDataInt::getNextProcess"

    return nextProcess;

def transferProcessToSequencedProcessList(processName):
    targetProcessIndex = 0
    # get index for target process
    targetProcessIndex = getTargetProcessIndex(processName)
    listElement = processes[targetProcessIndex]
    sequencedProcessListJson.append(listElement)
    processes.remove(listElement)

    if dbg:
        for i in range(0,len(processes)):
            print processes[i]["name"]

    if dbg:
        for i in range(0,len(sequencedProcessListJson)):
            print sequencedProcessListJson[i]["name"]

    if dbg: print "exiting: ComboDataInt::transferProcessToSequencedProcessList"


def addOutputConnectionsToDataReadyList(processName):
    #print "***********entering: ComboDataInt::addOutputConnectionsToDataReadyList*************"
    procIndex = getTargetProcessIndex(processName)

    if procIndex >= 0:
        for outputIndex in range(0,len(processes[procIndex]["outputs"])):
            tempConn = Connector()
            tempConn.process = processName
            tempConn.port = processes[procIndex]["outputs"][outputIndex]
            if dbg: print("appending %s:%s to dataReadyList" % (tempConn.process,tempConn.port))
            if isOutputInDataReadyList(tempConn) == False:
                dataReadyList.append(tempConn)

    if dbg:
        for i in range(0,len(dataReadyList)):
            print("dataReadyList[%d]: %s:%s" % (i,dataReadyList[i].process,dataReadyList[i].port))

        else:
            print "could not find named process: " + processName
    if dbg: print "exiting: ComboDataInt::addOutputConnectionsToDataReadyList"

def printDataReadyList():
    for i in range(0,len(dataReadyList)):
        print("dataReadyList[%d]: %s:%s" % (i,dataReadyList[i].process,dataReadyList[i].port))

def printUnsequencedProcessList():
    for i in range(0,len(processes)):
        print("processes[%d]: %s" % (i,processes[i]['name']))

def printSequencedProcessList():
    for i in range(0,len(sequencedProcessListJson)):
        print("sequencedProcessListJson[%d]: %s" % (i,sequencedProcessListJson[i]['name']))




def main():

    init_connections()
    fillUnsequencedProcessList()

    printUnsequencedProcessList()
    printSequencedProcessList()
    proc = getFirstProcess()
    if dbg: print "PROCESS: " + proc
    addOutputConnectionsToDataReadyList(proc)
    transferProcessToSequencedProcessList(proc)

    while isUnsequencedProcessListEmpty() == False:
        proc = getNextProcess(proc)
        if dbg: print "PROCESS: " + proc
        addOutputConnectionsToDataReadyList(proc)
        transferProcessToSequencedProcessList(proc)
        printDataReadyList()
        printUnsequencedProcessList()
        printSequencedProcessList()
        # print "*************LOOP END ******************"

if __name__ == "__main__":
   main()
