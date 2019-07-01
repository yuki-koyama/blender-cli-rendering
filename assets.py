import bpy
import utils

materials = {
    "Concrete07": {
        "color": "./assets/textures/[2K]Concrete07/Concrete07_col.jpg",
        "metallic": "",
        "roughness": "./assets/textures/[2K]Concrete07/Concrete07_rgh.jpg",
        "normal": "./assets/textures/[2K]Concrete07/Concrete07_nrm.jpg",
        "displacement": "./assets/textures/[2K]Concrete07/Concrete07_disp.jpg",
        "ambient_occlusion": "./assets/textures/[2K]Concrete07/Concrete07_AO.jpg"
    },
    "Fabric02": {
        "color": "./assets/textures/[2K]Fabric02/Fabric02_col.jpg",
        "metallic": "",
        "roughness": "./assets/textures/[2K]Fabric02/Fabric02_rgh.jpg",
        "normal": "./assets/textures/[2K]Fabric02/Fabric02_nrm.jpg",
        "displacement": "./assets/textures/[2K]Fabric02/Fabric02_disp.jpg",
        "ambient_occlusion": "",
    },
    "Leather05": {
        "color": "./assets/textures/[2K]Leather05/Leather05_col.jpg",
        "metallic": "",
        "roughness": "./assets/textures/[2K]Leather05/Leather05_rgh.jpg",
        "normal": "./assets/textures/[2K]Leather05/Leather05_nrm.jpg",
        "displacement": "./assets/textures/[2K]Leather05/Leather05_disp.jpg",
        "ambient_occlusion": "",
    },
    "Marble01": {
        "color": "./assets/textures/[2K]Marble01/Marble01_col.jpg",
        "metallic": "",
        "roughness": "./assets/textures/[2K]Marble01/Marble01_rgh.jpg",
        "normal": "./assets/textures/[2K]Marble01/Marble01_nrm.jpg",
        "displacement": "./assets/textures/[2K]Marble01/Marble01_disp.jpg",
        "ambient_occlusion": "",
    },
    "Metal07": {
        "color": "./assets/textures/[2K]Metal07/Metal07_col.jpg",
        "metallic": "./assets/textures/[2K]Metal07/Metal07_met.jpg",
        "roughness": "./assets/textures/[2K]Metal07/Metal07_rgh.jpg",
        "normal": "./assets/textures/[2K]Metal07/Metal07_nrm.jpg",
        "displacement": "./assets/textures/[2K]Metal07/Metal07_disp.jpg",
        "ambient_occlusion": "",
    },
}


def build_pbr_textured_nodes(node_tree, name, scale=(1.0, 1.0, 1.0)):
    utils.build_pbr_textured_nodes(node_tree,
                                   color_texture_path=materials[name]["color"],
                                   metallic_texture_path=materials[name]["metallic"],
                                   roughness_texture_path=materials[name]["roughness"],
                                   normal_texture_path=materials[name]["normal"],
                                   displacement_texture_path=materials[name]["displacement"],
                                   ambient_occlusion_texture_path=materials[name]["ambient_occlusion"],
                                   scale=scale)
