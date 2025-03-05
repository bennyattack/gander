import pyiec61850 as iec61850
import time
import sys
import argparse
from SCL import extract_goose_info
from SCL import format_ds_contents



def main():

    parser = argparse.ArgumentParser(description="Extract GOOSE information from a CID file.")
    parser.add_argument("cid_filename", type=str, help="Path to the CID file")
    args = parser.parse_args()
    
    goose_info = extract_goose_info(args.cid_filename)

    # all this will be populated using data from CIDex.py
    confrev=int(goose_info[0][5] )#1
    ied_name=goose_info[0][0] #"SS_H199B"   
    inst=goose_info[0][1] #"Master"
    gocb=goose_info[0][3] #"SS_H199B_GOCB1"
    dataset=goose_info[0][4] #"SS_H199B_GODS1"    
    ied_macaddress =goose_info[0][6].replace("-", ":") # "01:0C:CD:01:0B:03" # destination (Multicast) MAC Address
    goid=goose_info[0][2] #"SS_H199B_Trips"
    appid=goose_info[0][7] #"8103"
    vlan_id=int(goose_info[0][8]) # 153
    vlan_pri=int(goose_info[0][9]) # 4
    dataset_contents = goose_info[0][10]

    # construct CB and DS reference strings
    gocbref=ied_name+inst+"/LLN0$GO$"+gocb
    datasetref=ied_name+inst+"/LLN0$"+dataset   

    # display extract values
    print("gocbref:\t", gocbref)
    print("datasetref:\t", datasetref)
    print("MAC:\t\t", ied_macaddress)
    print("goid:\t\t", goid)
    print("confrev:\t", confrev)
    print("appid:\t\t", appid)
    print("vlan_id:\t", vlan_id)
    print("vlan_pri:\t", vlan_pri)
    print()
    print("dataset contents: ")
    for dataset_item in dataset_contents:
        print(format_ds_contents(dataset_item))
    
    
    numItems = len(dataset_contents)

    print("number of items in dataset: ", numItems)
    
    #quit()

    
###########################################################################################################



    #interface="enp2s0" # name of ethernet interface
    interface="lo"
    
  
    for i in range(3):  
        # create linked list for dataset items
        dataSetValues = iec61850.LinkedList_create()
       
        # add values to dataset
        for item in dataset_contents:
            if item[5] == 'stVal' or item[5] == 'general':
               iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBoolean(False))
               #print("Adding bType:Boolean...")
            if item[5] == 'q':
                iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newBitString(4))
                #print("Adding bType:Quality...")
            # iec61850.LinkedList_add(dataSetValues, iec61850.MmsValue_newIntegerFromInt32(5))

        print("Sending packet...")
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
