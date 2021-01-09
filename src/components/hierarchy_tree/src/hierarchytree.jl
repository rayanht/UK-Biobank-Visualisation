# AUTO GENERATED FILE - DO NOT EDIT

export hierarchytree

"""
    hierarchytree(;kwargs...)

A HierarchyTree component.

Keyword arguments:
- `id` (String; optional): The ID used to identify this component in Dash callbacks.
- `data` (Array; optional): The data displayed in the tree.
- `selected_nodes` (Array of Dicts; optional): An array of selected nodes
- `max_selections` (Real; optional): The maximum number of nodes that should be selected at any time
- `n_updates` (Real; optional): A count of the number of times the inputs have updated, so the callback function knows when to update
- `clopenState` (Bool | Real | String | Dict | Array; optional): The clopen state of the nodes in the tree.
"""
function hierarchytree(; kwargs...)
        available_props = Symbol[:id, :data, :selected_nodes, :max_selections, :n_updates, :clopenState]
        wild_props = Symbol[]
        return Component("hierarchytree", "HierarchyTree", "hierarchy_tree", available_props, wild_props; kwargs...)
end

