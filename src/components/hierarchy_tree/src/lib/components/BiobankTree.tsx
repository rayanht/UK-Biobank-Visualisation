import * as React from "react";
import {Classes, Icon, ITreeNode, Tree} from "@blueprintjs/core";
import "./Tree.css"


export interface IHierachyTreeNode extends ITreeNode {
    category_id?: number;
    field_id?: number;
    unselected_children?: IHierachyTreeNode[];
}

export interface IHierarchyTreeState {
    nodes: IHierachyTreeNode[];
    selected_nodes: IHierachyTreeNode[];
    n_updates: number;
    max_selections: number;
    setProps: Function;
    setClopenState: any;
}

// use Component so it re-renders every time: `nodes` are not a primitive type
// and therefore aren't included in shallow prop comparison
export class BiobankTree extends React.Component<IHierarchyTreeState> {
    public state: IHierarchyTreeState = {
        selected_nodes: this.props.selected_nodes,
        nodes: this.props.nodes,
        n_updates: this.props.n_updates,
        max_selections: this.props.max_selections,
        setProps: this.props.setProps,
        setClopenState: this.props.setClopenState,
    };

    componentDidUpdate(prevProps) {
        // Replace selected nodes by the new nodes, using previous ids, since the references were lost
        if (prevProps.nodes !== this.props.nodes) {
            const newSelected = prevProps.selected_nodes.map((n) => {
                const node = this.searchNodes(this.props.nodes, n.id.toString());
                if (node == undefined) {
                    return n;
                }
                return node;
            });
            for (const n of this.props.nodes) {
                this.keepSelected(n);
            }
            this.setState(prevState => ({...prevState, nodes: this.props.nodes, selected_nodes: newSelected}));
        }

        // Add a tick icon to all selected nodes
        this.forEachNode(this.props.nodes, (n) => {
            if (n.isSelected) {
                n.secondaryLabel = <Icon icon={"tick"}/>;
            }
        })
    }

    public render() {
        return (
            <Tree
                contents={this.state.nodes}
                onNodeClick={this.handleNodeClick}
                onNodeCollapse={this.handleNodeCollapse}
                onNodeExpand={this.handleNodeExpand}
                className={Classes.ELEVATION_0}
            />
        );
    }

    private handleNodeClick = (nodeData: IHierachyTreeNode, _nodePath: number[], e: React.MouseEvent<HTMLElement>) => {
        const originallySelected = nodeData.isSelected;

        // If the node isn't a leaf node just expand/collapse it and return
        if (nodeData.hasCaret) {
            if (nodeData.isExpanded) {
                this.handleNodeCollapse(nodeData);
            } else {
                this.handleNodeExpand(nodeData);
            }
            return;
        }

        nodeData.isSelected = originallySelected == null ? true : !originallySelected;

        // Add or remove a node from the selected list based on its previous state,
        // also adding or removing the tick icon
        if (nodeData.isSelected) {
            this.state.selected_nodes.push(nodeData);
            nodeData.secondaryLabel = <Icon icon={"tick"}/>;
            this.handleNodeExpand(nodeData);
        } else {
            const index = this.state.selected_nodes.indexOf(nodeData);
            if (index > -1) {
                this.state.selected_nodes.splice(index, 1)
                nodeData.secondaryLabel = null;
                this.handleNodeCollapse(nodeData);
            }
        }

        // If the number of selected items exceeds that of the max,
        // pop the oldest item from the list and unselect it
        if (this.state.selected_nodes.length > this.state.max_selections) {
            const first = this.state.selected_nodes[0];
            first.isSelected = false;
            first.secondaryLabel = null;
            this.handleNodeCollapse(first);
            this.state.selected_nodes.shift();
        }

        this.state.n_updates = this.state.n_updates + 1;

        // No need to update state here, since when the props are changed, the component will be re-rendered
        this.props.setProps(this.state);
    };

    private handleNodeCollapse = (nodeData: IHierachyTreeNode) => {
        // If the node doesn't have any 'unselected children', then it should be collapsed normally
        if (nodeData.unselected_children == undefined) {

            if (this.hasSelected(nodeData)) {
                this.changeSelectedNodeState(nodeData, this.handleNodeCollapse);

            // If this node doesn't contain any selected children, just collapse it normally
            } else {
                nodeData.isExpanded = false;
                this.state.setClopenState(nodeData.id, false);
            }

        // If the node already has 'unselected children',
        // we should instead add those children back to the node and sort them
        } else {
            nodeData.childNodes = nodeData.childNodes.concat(nodeData.unselected_children);
            nodeData.childNodes.sort(BiobankTree.sortByLabel)
            nodeData.unselected_children = undefined;
        }
        this.setState(this.state);
    }

    // Expand the node and sort its children alphabetically based on label
    private handleNodeExpand = (nodeData: IHierachyTreeNode) => {
        nodeData.isExpanded = true;
        if (nodeData.childNodes != undefined) {
            nodeData.childNodes.sort(BiobankTree.sortByLabel)
        }
        this.state.setClopenState(nodeData.id, true);
        this.setState(this.state);
    };

    // A custom comparator for tree nodes based on label alphabetical order
    private static sortByLabel(a: IHierachyTreeNode, b: IHierachyTreeNode) {
        return a.label > b.label ? 1 : a.label < b.label ? -1 : 0
    }

    // For every node (and all corresponding children) call the void callback
    private forEachNode(nodes: ITreeNode[], callback: (node: ITreeNode) => void) {
        if (nodes == null) {
            return;
        }

        for (const node of nodes) {
            callback(node);
            this.forEachNode(node.childNodes, callback);
        }
    }

    // Check if a node has a selected child at any depth
    private hasSelected(node: IHierachyTreeNode) {
        if (node.isSelected) {
            return true;
        }
        if (node.childNodes != null) {
            for (const n of node.childNodes) {
                if (this.hasSelected(n)) {
                    return true;
                }
            }
        }
        return false;
    }

    // Search all nodes for one with the given id, and return it
    private searchNodes(nodes: ITreeNode[], id: string) {
        if (nodes == null) {
            return;
        }

        for (const node of nodes) {
            if (node.id.toString() == id) {
                return node;
            }
            const n = this.searchNodes(node.childNodes, id);
            if (n != null) {
                return n;
            }
        }
    }

    private keepSelected = (nodeData: IHierachyTreeNode) => {
        if (this.hasSelected(nodeData) && !nodeData.isExpanded) {
            nodeData.isExpanded = true;
            this.changeSelectedNodeState(nodeData, this.keepSelected);
        }
    }

    private changeSelectedNodeState = (nodeData: IHierachyTreeNode, selectedFunction: (arg0: ITreeNode) => void) => {
        nodeData.unselected_children = []
        for (const child of nodeData.childNodes) {

            // If the node contains a selected node at any depth, handle those recursively with the given function.
            if (this.hasSelected(child)) {
                const c = child as IHierachyTreeNode
                if (child.childNodes != null && c.unselected_children == undefined) {
                    selectedFunction(child)
                }

            // All other nodes should be moved to the 'unselected_nodes' field of their parent
            } else {
                nodeData.unselected_children.push(child);
            }
        }

        // Remove all 'unselected nodes'
        for (const node of nodeData.unselected_children) {
            const index = nodeData.childNodes.indexOf(node);
            if (index > -1) {
                nodeData.childNodes.splice(index, 1);
            }
        }
        nodeData.childNodes.sort(BiobankTree.sortByLabel)
    }
}
