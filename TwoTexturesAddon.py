bl_info = {
    "name": "Procedural abstract material",
    "author": "Alan Adamiak",
    "version": (1, 0, 0),
    "blender": (2, 81, 0),
    "description": "Generate a random abstract material",
    "category": "Object",
}

import bpy
import random

class ProceduralAbstractMaterial(bpy.types.Operator):
    """Generate Material"""
    bl_idname = "object.generate_material"
    bl_label = "Generate Material"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Generate a random abstract material"
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    
    def execute(self, context):
        generateMaterial()
        return {'FINISHED'}

musgraveType = ['MULTIFRACTAL', 'RIDGED_MULTIFRACTAL', 'HYBRID_MULTIFRACTAL', 'FBM', 'HETERO_TERRAIN']
voronoiDistance = ['EUCLIDEAN', 'MANHATTAN', 'CHEBYCHEV', 'MINKOWSKI']
waveType = ['RINGS', 'BANDS']
waveProfile = ['SINE', 'SAW']

def randomVoronoi(mat_nodes):
    tex = mat_nodes.new('ShaderNodeTexVoronoi')
    tex.feature = 'SMOOTH_F1'
    tex.distance = random.choice(voronoiDistance)
    tex.inputs[2].default_value = random.uniform(2, 20)
    tex.inputs[3].default_value = random.uniform(0, 1)
    tex.inputs[4].default_value = random.uniform(0, 1)
    if tex.distance == 'MINKOWSKI':
        tex.inputs[4].default_value = random.uniform(0.3, 3)
        tex.inputs[5].default_value = random.uniform(0, 1);
    return tex     

def randomNoise(mat_nodes):
    tex = mat_nodes.new('ShaderNodeTexNoise')
    tex.inputs[1].default_value = random.uniform(2, 20)
    tex.inputs[2].default_value = random.uniform(1, 10)
    tex.inputs[3].default_value = random.uniform(0, 20)
    return tex

def randomMusgrave(mat_nodes):
    tex = mat_nodes.new('ShaderNodeTexMusgrave')
    tex.musgrave_type = random.choice(musgraveType)
    tex.inputs[1].default_value = random.uniform(2, 20)
    tex.inputs[2].default_value = random.uniform(0, 10)
    tex.inputs[3].default_value = random.uniform(0, 10)
    tex.inputs[4].default_value = random.uniform(0.5, 2)
    return tex

def randomWave(mat_nodes):
    tex = mat_nodes.new('ShaderNodeTexWave')
    tex.wave_type = random.choice(waveType)
    tex_profile = random.choice(waveProfile)
    tex.inputs[1].default_value = random.uniform(2, 10)
    tex.inputs[2].default_value = random.uniform(0, 50)
    tex.inputs[3].default_value = random.uniform(0, 20)
    tex.inputs[4].default_value = random.uniform(0, 2)
    return tex

def randomMagic(mat_nodes):
    tex = mat_nodes.new('ShaderNodeTexMagic')
    tex.turbulence_depth = random.randint(0, 10)
    tex.inputs[1].default_value = random.uniform(2, 10)
    tex.inputs[2].default_value = random.uniform(0, 2)
    return tex

def randomTexture(mat_nodes):
    r = random.randint(0, 4)
    if r == 0:
        return randomVoronoi(mat_nodes)
    elif r == 1:
        return randomNoise(mat_nodes)
    elif r == 2:
        return randomMusgrave(mat_nodes)
    elif r == 3:
        return randomWave(mat_nodes)
    else:
        return randomMagic(mat_nodes)

def generateMaterial():
    activeObject = bpy.context.active_object
    bpy.ops.object.material_slot_remove()
    mat = bpy.data.materials.new(name='Abstract Material')
    mat.use_nodes = True
    mat_nodes = mat.node_tree.nodes
    mat_nodes.remove(mat_nodes.get('Principled BSDF'))
    mat_links = mat.node_tree.links
    
    output = mat_nodes['Material Output']
    output.location = (330, 310)
    
    glossy = mat_nodes.new(type='ShaderNodeBsdfGlossy')
    glossy.location = (150, 400)
    mat_links.new(output.inputs[0], glossy.outputs[0])
    
    displacement = mat_nodes.new('ShaderNodeDisplacement')
    displacement.location = (150, 240)
    mat_links.new(output.inputs[2], displacement.outputs[0])
    
    voronoi = randomVoronoi(mat_nodes)
    voronoi.location = (-30, 240)
    mat_links.new(displacement.inputs[2], voronoi.outputs[0])
    
    tex = randomTexture(mat_nodes)
    tex.location = (-210, 240)
    mat_links.new(voronoi.inputs[0], tex.outputs[0])
    
    colorRamp = mat_nodes.new('ShaderNodeValToRGB')
    colorRamp.location = (-125, 450)
    colorRamp.color_ramp.elements[1].position = 0.75
    mat_links.new(glossy.inputs[1], colorRamp.outputs[0])
    
    fresnel = mat_nodes.new('ShaderNodeFresnel')
    fresnel.location = (-300, 350)
    fresnel.inputs[0].default_value = 2
    mat_links.new(colorRamp.inputs[0], fresnel.outputs[0])
    
    activeObject.data.materials.append(mat)

def menu_func(self, context):
    self.layout.operator(ProceduralAbstractMaterial.bl_idname)
    
def register():
    bpy.utils.register_class(ProceduralAbstractMaterial)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.utils.unregister_class(ProceduralAbstractMaterial)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()