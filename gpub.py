import pyiec61850 as iec61850
import time
import sys

def main():

    # all this will be populated using data from CIDex.py
    confrev = 1
    ied_name="SS_H199B"   
    inst="Master"
    gocb="SS_H199B_GOCB1"
    dataset="SS_H199B_GODS1"    
    ied_macaddress = "01:0C:CD:01:0B:03" # destination (Multicast) MAC Address
    goid="SS_H199B_Trips"
    appid="8103"
    vlan_id = 153
    vlan_pri = 4
    # construct CB and DS reference strings
    gocbref=ied_name+inst+"/LLN0$GO$"+gocb
    datasetref=ied_name+inst+"/LLN0$"+dataset   

    interface="enp2s0" # name of ethernet interface
    
    numItems = 13
  
    for i in range(numItems):  
        # create linked list for dataset items
        dataSetValues = iec61850.LinkedList_create()
        
        # create list to hold dummy values for dataset
        switches = []
        for j in range(numItems):
            val = True if j == i else False
            switches.append(val) 

        # display values which will be published 
        print("Values in packet #", str(i+1), ":\t", sep='', end='')
        print(switches)
        
        # dump values from switch list into Dataset
        for k in range(numItems):
            iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBoolean(switches[k]))
            iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBitString(4))
            # iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newIntegerFromInt32(5))

           
        gooseCommParameters = iec61850.CommParameters()

        gooseCommParameters.appId = int(appid, 16)
        gooseCommParameters.vlanId = vlan_id
        gooseCommParameters.vlanPriority = vlan_pri

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
