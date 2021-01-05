from . import colour_selection
from . import range_filter
from . import graph_type
from . import instance_selection
from . import plot
from . import trendline
from . import variable_selection


# Function for selecting setting
def get_setting(encoding, arg=None):
    return _get_option_switcher[encoding](arg)


_get_option_switcher = {
    "colour": colour_selection.get_option_dropdown,
    "instance": instance_selection.get_option_dropdown,
    "variable": variable_selection.get_option_dropdown,
    "filter": range_filter.get_option_dropdown,
    "graph_type": graph_type.get_option_dropdown,
    "trendline": trendline.get_trendline_dropdown,
    "plot_graph": plot.get_button,
}
