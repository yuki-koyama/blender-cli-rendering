Warning: the following requirements are not fully satisfied in the current scripts. This issue needs to be fixed.

## Formatting

PEP8 with an exception of using 120-column-limit.

`yapf` users can easily ensure this rule by the following command:
```
find . -name "*.py" | xargs -I {} yapf --style='{based_on_style: pep8, column_limit: 120}' -i {}
```

Useful link: <https://wiki.blender.org/wiki/Style_Guide/Python>

## Typing

```
mypy *.py --ignore-missing-import --strict --implicit-reexport
```

Note that the current codes do not satisfy this above condition. This needs to be fixed.

## Naming Conventions

### Functions

- A function named `create_XXX` instantiates an `bpy.types.Object`/`bpy.types.Node` to the specified `scene`/`node_tree`. This function returns the newly created `bpy.types.Object`/`bpy.types.Node`.
- A function named `create_XXXs` instantiates a set of `bpy.types.Object`/`bpy.types.Node` to the specified `scene`/`node_tree`. This function returns a tuple of the newly created `bpy.types.Object`/`bpy.types.Node`.
- A function named `build_XXX` manipulates the specified `scene`/`node_tree` by various operations; for example, by instantiating a set of objects. This function does not return anything.
- A function named `set_XXX` changes parameters of specified objects etc. This function does not instantiate new objects. This function does not return anything.
- A function named `add_XXX_constraint`/`modifier` adds either a constraint or modifier to an object. This function does not instantiate new objects. This function does not return anything.
- A function named `add_XXX_YYY` adds a data-block to data-blocks in `bpy.data.YYYs`. This function does not instantiate any `bpy.types.Object`/`bpy.types.Node` to `scene`/`node_tree`. This function returns the newly added `YYY`.

### Variables

- A variable named `XXX_object` (or `object`) has the type `bpy.types.Object`. In addition, an instance of `bpy.types.Object` that has its `type` of `YYY` (e.g., `Mesh`) should have a name like `XXX_YYY_object` (e.g., `cube_mesh_object`).
- A variable named `XXX_node` (or `node`) has the type `bpy.types.Node`.
- An instance of a subclass of `bpy.types.ID`, say `bpy.type.Camera` for example, should have a name like `XXX_camera`.
