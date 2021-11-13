import math
import sys
import time
import threading

config = None
Exit = 0

MB=1000000

def convert_to_blocks(file_name,block_size):
    f=open(file_name,'rb')
    tot_bytes=0
    for l in f:
        tot_bytes+=sys.getsizeof(l)
    tot_mb=tot_bytes/MB
    tot_splits=math.ceil(tot_mb/block_size)
    return tot_splits

def sendMsg(Queue, Lock, Data):
    
    print("namenode sent", Data[0])
    Lock.acquire(block = True)
    Queue.put(Data)
    Lock.release()

def receiveMsg(Queue, Lock):
    
    if(Lock.acquire(block = True)):

        Message = [1, None]

        if(Queue.empty() != True):
            
            Message = Queue.get()
            print("namenode rcvd", Message[0])
        
        Lock.release()

        if(Message[0] == 0):
            return 0
        elif(Message[0] == 100):
            return 100
        elif(Message[0] == 101):
            global config
            config = Message[1]
            return 101
        else:
            return 1
    
    else:
        return 1

def master(MQueue, MLock, NNQueue, NNLock, SNNQueue, SNNLock):
    
    while(Exit != 1):
        
        Code = receiveMsg(NNQueue, NNLock)

        if(Code == 100):
            sendMsg(MQueue, MLock, [100, None])
        elif(Code == 101):
            SecondaryNNSync = threading.Thread(target = SNNSync, args = (MQueue, MLock, SNNQueue, SNNLock))
            SecondaryNNSync.start()
        elif(Code == 0):
            SecondaryNNSync.join()

def SNNSync(MQueue, MLock, SNNQueue, SNNLock):

    sendMsg(MQueue, MLock, [102, None])

    while(Exit != 1):
        sendMsg(SNNQueue, SNNLock, [103, None])
        time.sleep(config["sync_period"])