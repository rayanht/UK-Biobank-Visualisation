/*
 * Copyright 2015 Palantir Technologies, Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import * as React from "react";
import {Classes, Icon, ITreeNode, Tree} from "@blueprintjs/core";
import "./Tree.css"

export interface IHierachyTreeNode extends ITreeNode {
    category_id?: number;
    field_id?: number;
}

export interface ITreeExampleState {
    nodes: IHierachyTreeNode[];
    selected_nodes: IHierachyTreeNode[];
    n_updates: number;
    max_selections: number;
    setProps: Function;
    setClopenState: any;
}

// use Component so it re-renders everytime: `nodes` are not a primitive type
// and therefore aren't included in shallow prop comparison
export class TreeExample extends React.Component<ITreeExampleState> {
    public state: ITreeExampleState = {
        selected_nodes: this.props.selected_nodes,
        nodes: this.props.nodes,
        n_updates: this.props.n_updates,
        max_selections: this.props.max_selections,
        setProps: this.props.setProps,
        setClopenState: this.props.setClopenState
    };

    componentDidUpdate(prevProps) {
        if (prevProps.nodes !== this.props.nodes) {
            const newSelected = prevProps.selected_nodes.map(n => this.searchNodes(this.props.nodes, n.id.toString()));
            this.setState(prevState => ({...prevState, nodes: this.props.nodes, selected_nodes: newSelected}));
        }
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
        nodeData.isExpanded = false;
        this.state.setClopenState(nodeData.id, false);
        this.setState(this.state);
    };

    private handleNodeExpand = (nodeData: IHierachyTreeNode) => {
        nodeData.isExpanded = true;
        this.state.setClopenState(nodeData.id, true);
        this.setState(this.state);
    };

    private forEachNode(nodes: ITreeNode[], callback: (node: ITreeNode) => void) {
        if (nodes == null) {
            return;
        }

        for (const node of nodes) {
            callback(node);
            this.forEachNode(node.childNodes, callback);
        }
    }

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
}
