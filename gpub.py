import pyiec61850 as iec61850
import time
import sys

def main():

    confrev = 1
    # Destination (Multicast) MAC Address
    ied_macaddress = "01:0C:CD:01:0B:03"
    ied_name="GOOSE_PUBL"
    #App ID
    appid="0B03"
    # GOOSE Control Block 
    gocbref='GOOSE_PUBLTO_RCU22001/LLN0$GO$RCU22001_GrAct' 
    # e.g. SS_G199AApplication/LLN0$GO$SS_G199A_GOCB1
    # GOOSE Dataset Reference
    datasetref='GOOSE_PUBLTO_RCU22001/LLN0$Dataset1' 
    # e.g. SS_G199AApplication/LLN0$SS_G199A_GODS1
    #GOOSE ID
    goid="RCU22001_GrAct" 
    # e.g. SS_G199A_Trips
    
    interface="enp2s0" 

    

    numItems = 13

    # iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newIntegerFromInt32(5))

    for i in range(numItems):  
        # create linked list for dataset items
        dataSetValues = iec61850.LinkedList_create()
        
        # create list to hold dummy values for dataset
        switches = []
        for j in range(numItems):
            val = True if j == i else False
            switches.append(val) 

        print("Values in packet #", str(i+1), ": ", sep='', end='')
        print(switches)
        
        # dump values from switch list into Dataset
        for k in range(numItems):
            iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBoolean(switches[k]))
            iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBitString(4))
    
            
        gooseCommParameters = iec61850.CommParameters()

        gooseCommParameters.appId = int(appid, 16)
        gooseCommParameters.vlanId = 0
        gooseCommParameters.vlanPriority = 4

        hex_parts = ied_macaddress.split(":")
        dst_mac_address = [int(part, 16) for part in hex_parts]

        iec61850.CommParameters_setDstAddress(gooseCommParameters, *dst_mac_address)

        publisher = iec61850.GoosePublisher_create(gooseCommParameters, interface)

        if (publisher):
            iec61850.GoosePublisher_setGoCbRef(publisher, gocbref)
            iec61850.GoosePublisher_setConfRev(publisher, confrev)
            iec61850.GoosePublisher_setDataSetRef(publisher, datasetref)
            iec61850.GoosePublisher_setTimeAllowedToLive(publisher, 2000) # 2000 for IED, 4000 for MU
            iec61850.GoosePublisher_setGoID(publisher, goid)

            for j in range(1):
                if (iec61850.GoosePublisher_publish(publisher, dataSetValues) == -1):
                    print("Error sending message!\n")
                time.sleep(1)

            iec61850.GoosePublisher_destroy(publisher)

        else:
            print("Failed to create GOOSE publisher. Reason can be that the Ethernet interface doesn't exist or root permission are required.\n")
            response = input("Enter 'r' to retry or hit enter to exit: ")
            if(response != 'r'):
                exit()
            

        iec61850.LinkedList_destroyDeep_MmsValueDelete(dataSetValues)

    exit()

if __name__ == "__main__":
    main()
