# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class HierarchyTree(Component):
    """A HierarchyTree component.


Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks.
- data (list; optional): The data displayed in the tree.
- selected_nodes (list of dicts; optional): An array of selected nodes
- max_selections (number; optional): The maximum number of nodes that should be selected at any time
- n_updates (number; optional): A count of the number of times the inputs have updated, so the callback function knows when to update
- clopenState (boolean | number | string | dict | list; optional): The clopen state of the nodes in the tree."""

    @_explicitize_args
    def __init__(
        self,
        id=Component.UNDEFINED,
        data=Component.UNDEFINED,
        selected_nodes=Component.UNDEFINED,
        max_selections=Component.UNDEFINED,
        n_updates=Component.UNDEFINED,
        clopenState=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "data",
            "selected_nodes",
            "max_selections",
            "n_updates",
            "clopenState",
        ]
        self._type = "HierarchyTree"
        self._namespace = "hierarchy_tree"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "data",
            "selected_nodes",
            "max_selections",
            "n_updates",
            "clopenState",
        ]
        self.available_wildcard_properties = []

        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(HierarchyTree, self).__init__(**args)
