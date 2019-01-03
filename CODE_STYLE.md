Warning: the following requirements are not fully satisfied in the current scripts. This issue needs to be fixed.

## Formatting

- Tab indent

## Naming Conventions

- A function named `create_XXX` instantiates an `object`/`node` to the specified `scene`/`node_tree`. This function returns the newly created `object`/`node`.
- A function named `build_XXX` manipulates the specified `scene`/`node_tree` by various operations; for example, by instantiating a set of objects. This function does not return anything.
- A function named `set_XXX` changes parameters of specified objects etc. This function does not instantiate new objects. This function does not return anything.
- A function named `add_XXX` adds either constraints or modifiers to an object. This function does not instantiate new objects. This function does not return anything.
- A function named `define_XXX` adds some data to `bpy.data` but does not instantiate any `object`/`node`.
