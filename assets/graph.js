// const dfd = require("danfojs-node")

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        draw_graph: function(graph_data) {
            // df = new dfd.DataFrame(graph_data)
            // df.print()
            return "Hello!"
        }
    }
});
