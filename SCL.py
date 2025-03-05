# import .cid file and extract required information for publishing siumulated GOOSE messages (TxGOOSE)
# Another function could be written to extract RxGOOSE information at a later stage.

import xml.etree.ElementTree as ET
import argparse
from tabulate import tabulate

def extract_goose_info(cid_file):
    # Parse the XML file
    tree = ET.parse(cid_file)
    root = tree.getroot()
    
    # Define the namespace (commonly used in SCL files)
    ns = {'scl': 'http://www.iec.ch/61850/2003/SCL'}
    
    # Find all GOOSE control blocks
    txgoose_data = []
    for gcb in root.findall(".//scl:GSEControl", ns):
        goose_id = gcb.get("appID", "N/A")
        gcb_name = gcb.get("name", "N/A")
        dataset = gcb.get("datSet", "N/A")
        confrev = gcb.get("confRev", "N/A")
        
        # Initialize extracted fields
        mac = "N/A"
        vlan_id = "N/A"
        vlan_priority = "N/A"
        appid = "N/A"
        ied_name = "N/A"
        inst = "N/A"
        dataset_contents = []
        
        if gcb_name != "N/A":
            # Search for corresponding GSE element in the SubNetwork area
            for subnetwork in root.findall(".//scl:SubNetwork", ns):
                for connected_ap in subnetwork.findall("scl:ConnectedAP", ns):
                    ied_name = connected_ap.get("iedName", "N/A")
                    for gse in connected_ap.findall("scl:GSE", ns):
                        if gse.get("cbName") == gcb_name:
                            inst = gse.get("ldInst")
                            address = gse.find("scl:Address", ns)
                            if address is not None:
                                for p in address.findall("scl:P", ns):
                                    if p.get("type") == "MAC-Address":
                                        mac = p.text
                                    elif p.get("type") == "VLAN-ID":
                                        vlan_id = p.text
                                    elif p.get("type") == "VLAN-PRIORITY":
                                        vlan_priority = p.text
                                    elif p.get("type") == "APPID":
                                        appid = p.text
            
            # Discard entry if gcb_name does not start with ied_name
            # this filters out RxGOOSE entries
            if not gcb_name.startswith(ied_name):
                continue
            # discard entry if goose control block is not initialised
            if inst == "N/A":
                continue
            
            # Search for dataset contents
            for dataset_elem in root.findall(".//scl:DataSet", ns):
                if dataset_elem.get("name") == dataset:
                    for fcda in dataset_elem.findall("scl:FCDA", ns):
                        if True: #fcda.get('daName', 'N/A') != 'q':
                            dataset_contents.append(
                            [fcda.get('ldInst', 'N/A'),fcda.get('prefix', ''),fcda.get('lnClass', ''), fcda.get('lnInst', ''), fcda.get('doName', 'N/A'), fcda.get('daName', 'N/A'), fcda.get('fc', 'N/A')])
    
        
        # Store extracted data
        txgoose_data.append([
            ied_name,   # [0]
            inst,
            goose_id,
            gcb_name,   # [3]
            dataset,    # [4]
            confrev,
            mac,
            "0x" + appid if appid != "N/A" else appid,                  # display as hex
            str(int(vlan_id, 16)) if vlan_id != "N/A" else vlan_id,     # convert to dec
            vlan_priority,
            dataset_contents
        ])
    
    return txgoose_data

def format_ds_contents(item):
    output = str(item[0])+'/'+str(item[1])+str(item[2])+str(item[3])+'.'+str(item[4])+'.'+str(item[5])+' ('+str(item[6])+')'
    return output


