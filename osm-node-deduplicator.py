import xml.etree.ElementTree as ET
import os
import shutil

osm_file = input("OSM file: ")

# new filename
file_name, file_extension = os.path.splitext(osm_file)
new_osm_file = f"{file_name}_unduplicated{file_extension}"

# make copy
shutil.copy2(osm_file, new_osm_file)

tree = ET.parse(new_osm_file)
root = tree.getroot()

# dict with node id, coords
node_coords = {}

for node in root.findall('node'):
    node_id = node.get('id')
    lat = float(node.get('lat'))
    lon = float(node.get('lon'))
    node_coords[node_id] = (lat, lon)

nodes_to_delete = set()

# check proximity
for node_id, (lat, lon) in node_coords.items():
    for other_id, (other_lat, other_lon) in node_coords.items():
        if node_id != other_id and node_id not in nodes_to_delete and other_id not in nodes_to_delete:
            if (abs(lat - other_lat) < 0.0000001 and abs(lon - other_lon) < 0.0000001):
                # Mark only the node with the higher ID for deletion
                node_to_delete = max(node_id, other_id)
                nodes_to_delete.add(node_to_delete)
                print(f"Nodes {node_id} and {other_id} are too close. {node_to_delete} will be deleted.")

# delete close nodes
for node in root.findall('node'):
    if node.get('id') in nodes_to_delete:
        root.remove(node)
        print(f"Deleted node {node.get('id')}")

# delete references to deleted nodes
existing_node_ids = set(node.get('id') for node in root.findall('node'))
for way in root.findall('way'):
    for nd in way.findall('nd'):
        if nd.get('ref') not in existing_node_ids:
            way.remove(nd)
            print(f"Cleared removed node from way: {nd.get('ref')} out of {way.get('id')}")

tree.write(new_osm_file)
print(f"File with unduplicated nodes created: {new_osm_file}")
