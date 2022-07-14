
import json
import trimesh
import networkx as nx
from collections import defaultdict
import copy
import os
import numpy as np

partnet_geo_path = os.path.join('partnet/geo')
partnet_precomputed_path = os.path.join('partnet/precomputed')

class Part:
    def __init__(self):
        self.mesh = None
        self.type = None
        self.axis = None
        self.center = None
        self.range_a = None
        self.range_b = None

class Node:
    def __init__(self):
        self.id = None
        self.objs = []

def merge2mesh(mesh1, mesh2):
    new_mesh = copy.deepcopy(mesh1)
    shifted_mesh2_faces = copy.deepcopy(mesh2.faces) + copy.deepcopy(mesh1.vertices.shape[0])
    new_mesh.faces = np.concatenate((copy.deepcopy(mesh1.faces), copy.deepcopy(shifted_mesh2_faces)))
    new_mesh.vertices = np.concatenate((copy.deepcopy(mesh1.vertices), copy.deepcopy(mesh2.vertices)))
    return new_mesh

def merge_meshes(meshes):
    if len(meshes) == 0:
        return None
    base_mesh = meshes[0]
    face_labels = [0]*len(base_mesh.faces)
    for i in range(1, len(meshes)):
        base_mesh = merge2mesh(base_mesh, meshes[i])
        face_labels += [i]*len(meshes[i].faces)
    return base_mesh, face_labels

def recur_build_dict(node_jo, id2node):

    if 'children' not in node_jo:
        if 'objs' in node_jo:
            node = Node()
            node.id = node_jo['id']
            node.objs = node_jo['objs']
            id2node[node.id] = node
        return 

    for c_jo in node_jo['children']:
        recur_build_dict(c_jo, id2node) 

def build_dict(json_filename):
    id2node = defaultdict()
    with open(json_filename) as json_file:
        jo = json.load(json_file)
        if 'children' not in jo[0]:
            if 'objs' in jo[0]:
                node = Node()
                node.id = jo[0]['id']
                node.objs = jo[0]['objs']
                id2node[node.id] = node
            return id2node

        for c_jo in jo[0]['children']:
            recur_build_dict(c_jo, id2node)

    return id2node


def load_mesh(obj_filename):
    tri_obj = trimesh.load_mesh(obj_filename)
    if tri_obj.is_empty:
        return None
    if type(tri_obj) is trimesh.scene.scene.Scene:
        tri_mesh = tri_obj.dump(True)
    else:
        tri_mesh = tri_obj

    return tri_mesh

def get_parts_graph_from_file(precomputed_json_file):
    graph = nx.Graph()
    with open(precomputed_json_file) as json_file:
        conn_graph = json.load(json_file)['connectivityGraph']
        for si in range(len(conn_graph)):
            graph.add_node(si)
            for ei in conn_graph[si]:
                e_tuple = (si, ei)
                graph.add_edge(*e_tuple)

    return graph

def get_parts_from_file(precomputed_json_file, geo_path, id2node):
    
    parts = []

    mesh_path = os.path.join(geo_path, 'textured_objs')
    mobility_file = os.path.join(geo_path, 'mobility_v2.json')
    precomputed_part_infos = json.load(open(precomputed_json_file))['parts']
    mobility_part_infos = json.load(open(mobility_file))

    for part_index in range(len(precomputed_part_infos)):
        
        part = Part()
        precomputed_part_info = precomputed_part_infos[part_index]
        node_jos = precomputed_part_info['ids']
        meshes = []
        for node_id in node_jos:
            node = id2node[node_id]
            for obj in node.objs:
                mesh = load_mesh(os.path.join(mesh_path, obj + '.obj'))
                meshes.append(mesh)
        part_mesh, _ = merge_meshes(meshes)

        part.mesh = part_mesh
        part.type = mobility_part_infos[part_index]['joint']
        if bool(mobility_part_infos[part_index]['jointData']):
            part.axis = mobility_part_infos[part_index]['jointData']['axis']['direction']
            part.center = mobility_part_infos[part_index]['jointData']['axis']['origin']
            part.range_a = mobility_part_infos[part_index]['jointData']['limit']['a']
            part.range_b = mobility_part_infos[part_index]['jointData']['limit']['b']

        print('part', part.type, part.axis, part.center, part.range_a, part.range_b)
        parts.append(part)

    return parts

def process_shape(shape_id):
    id2node = build_dict(os.path.join(partnet_geo_path, shape_id, 'result.json'))
    parts = get_parts_from_file(os.path.join(partnet_precomputed_path, shape_id + '.artpre.json'), os.path.join(partnet_geo_path, shape_id), id2node)
    part_graph = get_parts_graph_from_file(os.path.join(partnet_precomputed_path, shape_id + '.artpre.json'))
    return parts, part_graph

if __name__ == "__main__":
    shape_id = '148'
    parts, part_graph = process_shape(shape_id)
    print('part_graph', part_graph.edges)

