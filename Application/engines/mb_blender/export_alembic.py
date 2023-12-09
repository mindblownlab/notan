import bpy
import os

seq = "SC01"
shot = "SHOT_010"
filename = "cam_shot_010"
anima = True
type = "abc"
file_path = str("L:/_JOBSATIVOS/666_GAR_FRE_chaos/2.PROD/3.3D/9.MAYA/cache/alembic/scenes/{0}/{1}/reference/{2}.v002.{3}").format(seq, shot, filename, type)

if not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))

if type == "obj":
    bpy.ops.export_scene.obj(
     filepath=file_path,
     check_existing=False,
     axis_forward='-Z',
     axis_up='Y',
     filter_glob="*.obj",
     use_selection=True,
     use_animation=False,
     use_mesh_modifiers=True,
     use_edges=True,
     use_smooth_groups=False,
     use_smooth_groups_bitflags=False,
     use_normals=True,
     use_uvs=True,
     use_materials=False,
     use_triangles=False,
     use_nurbs=False,
     use_vertex_groups=False,
     use_blen_objects=True,
     group_by_object=False,
     group_by_material=False,
     keep_vertex_order=False,
     global_scale=1,
     path_mode='AUTO'
    )

if type == "abc":
    if anima:
        bpy.ops.wm.alembic_export(filepath=file_path, vcolors=True, selected=True, start=bpy.context.scene.frame_start, end=bpy.context.scene.frame_end)
    else:
        bpy.ops.wm.alembic_export(filepath=file_path, vcolors=True, selected=True, start=1, end=1)

if type == "fbx":
    bpy.ops.export_scene.fbx(filepath = file_path, use_selection = True, bake_anim = True)