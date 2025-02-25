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
    goose_data = []
    for gcb in root.findall(".//scl:GSEControl", ns):
        appid = gcb.get("appID", "N/A")
        name = gcb.get("name", "N/A")
        dataset = gcb.get("datSet", "N/A")
        
        # Initialize extracted fields
        mac = "N/A"
        vlan_id = "N/A"
        vlan_priority = "N/A"
        extracted_appid = "N/A"
        ied_name = "N/A"
        
        if name != "N/A":
            # Search for corresponding GSE element in the SubNetwork area
            for subnetwork in root.findall(".//scl:SubNetwork", ns):
                for connected_ap in subnetwork.findall("scl:ConnectedAP", ns):
                    ied_name = connected_ap.get("iedName", "N/A")
                    for gse in connected_ap.findall("scl:GSE", ns):
                        if gse.get("cbName") == name:
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
                                        extracted_appid = p.text
            
            # Discard entry if name does not start with ied_name
            if not name.startswith(ied_name):
                continue
        
        # Store extracted data
        goose_data.append([
            appid,
            name,
            dataset,
            mac,
            vlan_id,
            vlan_priority,
            extracted_appid,
            ied_name
        ])
    
    return goose_data

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract GOOSE information from a CID file.")
    parser.add_argument("cid_filename", type=str, help="Path to the CID file")
    args = parser.parse_args()
    
    goose_info = extract_goose_info(args.cid_filename)
    
    # Print the extracted GOOSE information in a table format
    headers = ["IED Name", "Application", "GCB Name", "Dataset", "APPID", "MAC Address", "VLAN ID", "VLAN Priority"]
    print(tabulate(goose_info, headers=headers, tablefmt="grid"))
