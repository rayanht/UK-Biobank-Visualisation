
module HierarchyTree
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("hierarchytree.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "hierarchy_tree",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "hierarchy_tree.min.js",
    external_url = "https://unpkg.com/hierarchy_tree@0.0.1/hierarchy_tree/hierarchy_tree.min.js",
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "hierarchy_tree.min.js.map",
    external_url = "https://unpkg.com/hierarchy_tree@0.0.1/hierarchy_tree/hierarchy_tree.min.js.map",
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
