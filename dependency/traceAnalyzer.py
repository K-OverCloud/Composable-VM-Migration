'''
Created on Feb 7, 2017

@author: Jargal
'''

file_path = ""
VMs = []

f = open(file_path, 'r')


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

q = Queue()
for i in range(len(VMs)):
    VM = VMs[i]
    q.enqueue(VM)

lines = f.readlines()
    
dataSize = 0

for j in range(len(VMs)):
    source = q.items[q.size()-1]
    q.dequeue()

    for destination in q.items:
        
        for line in lines:
            raw_line = line.split(" ")
            packetType = raw_line[1]
            if packetType == "IP":
                sourceRaw = raw_line[2]
                destinationRaw = raw_line[4]
                packetLength = raw_line[13]
                if sourceRaw == source and destinationRaw == destination+":":
                    dataSize = dataSize + int(packetLength)
        
        print "Source: %s  Destination: %s  Data Size: %d" %(source, destination, dataSize)
        
        dataSize = 0
    q.enqueue(source)
     
f.close()

