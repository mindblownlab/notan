bl_info = {
    "name": "Importar múltiplos arquivos Alembic",
    "author": "Cabral",
    "version": (4, 0),
    "blender": (2, 93, 0),
    "location": "File > Import",
    "description": "Importar múltiplos arquivos Alembic de uma vez",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class ImportMultipleAlembic(Operator, ImportHelper):
    bl_idname = "import_multiple_alembic.abc"
    bl_label = "Import Multiple Alembic"
    
    # ImportHelper mixin class uses this
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        # Itera sobre a lista de arquivos .abc e importa cada um
        for file in self.files:
            path_to_abc = os.path.join(self.directory, file.name)
            bpy.ops.wm.alembic_import(filepath=path_to_abc)

            # Cria um objeto vazio e torna todos os objetos importados filhos desse objeto vazio
            empty = bpy.data.objects.new("empty", None)
            bpy.context.collection.objects.link(empty)

            for obj in bpy.context.selected_objects:
                obj.parent = empty
                
            # Escala o objeto vazio, efetivamente escalando todos os objetos Alembic
            empty.scale = (0.01, 0.01, 0.01)
            
        return {'FINISHED'}
    

def menu_func_import(self, context):
    self.layout.operator(ImportMultipleAlembic.bl_idname, text="Mult Alembic Import (.abc)")

def register():
    bpy.utils.register_class(ImportMultipleAlembic)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(ImportMultipleAlembic)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
