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
        dataset_contents = []
        
        if gcb_name != "N/A":
            # Search for corresponding GSE element in the SubNetwork area
            for subnetwork in root.findall(".//scl:SubNetwork", ns):
                for connected_ap in subnetwork.findall("scl:ConnectedAP", ns):
                    ied_name = connected_ap.get("iedName", "N/A")
                    for gse in connected_ap.findall("scl:GSE", ns):
                        if gse.get("cbName") == gcb_name:
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
            
            # Search for dataset contents
            for dataset_elem in root.findall(".//scl:DataSet", ns):
                if dataset_elem.get("name") == dataset:
                    for fcda in dataset_elem.findall("scl:FCDA", ns):
                        if fcda.get('daName', 'N/A') != 'q':
                            dataset_contents.append(
                            f"{fcda.get('ldInst', 'N/A')}/{fcda.get('prefix', '')}{fcda.get('lnClass', '')}{fcda.get('lnInst', '')}.{fcda.get('doName', 'N/A')}.{fcda.get('daName', 'N/A')} ({fcda.get('fc', 'N/A')})"
                        )
        
        # Store extracted data
        txgoose_data.append([
            ied_name,
            goose_id,
            gcb_name,
            dataset,
            confrev,
            mac,
            appid,
            vlan_id,
            vlan_priority,
            "\n".join(dataset_contents) if dataset_contents else "N/A"
        ])
    
    return txgoose_data

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GOOSE information from a CID file.")
    parser.add_argument("cid_filename", type=str, help="Path to the CID file")
    args = parser.parse_args()
    
    goose_info = extract_goose_info(args.cid_filename)
    
    # Print the extracted GOOSE information in a table format
    headers = ["IED Name", "GOOSE ID", "GCB Name", "Dataset", "ConfRev", "MAC Address", "APPID", "VLAN ID", "VLAN Pri.", "Dataset Contents"]
    print(tabulate(goose_info, headers=headers, tablefmt="grid"))
