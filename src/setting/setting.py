# Settings to be used
from src.setting.colour_setting import get_option_dropdown as get_colour_setting
from src.setting.instance_setting import get_option_dropdown as get_instance_setting
from src.setting.variable_setting import get_option_dropdown as get_variable_setting
from src.setting.filter_setting import get_option_dropdown as get_filter_setting
from src.setting.graph_type_setting import get_option_dropdown as get_graph_type_setting
from src.setting.trendline_setting import get_trendline_dropdown as get_graph_trendline_setting
from src.setting.plot_graph_setting import get_button as get_plot_graph_setting

# Function for selecting setting
def get_setting(encoding, arg=None):
    return _get_option_switcher[encoding](arg)


_get_option_switcher = {
    "colour": get_colour_setting,
    "instance": get_instance_setting,
    "variable": get_variable_setting,
    "filter": get_filter_setting,
    "graph_type": get_graph_type_setting,
    "trendline": get_graph_trendline_setting,
    "plot_graph": get_plot_graph_setting,
}