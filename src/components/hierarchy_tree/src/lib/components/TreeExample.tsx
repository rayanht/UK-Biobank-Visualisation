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

import {Classes, Icon, Intent, ITreeNode, Position, Tooltip, Tree} from "@blueprintjs/core";
import "./Tree.css"
import {node} from "prop-types";

export interface IHierachyTreeNode extends ITreeNode {
    catId?: number;
    fieldId?: number;
}

export interface ITreeExampleState {
    nodes: IHierachyTreeNode[];
    selected: Number[];
    n_updates: number;
    setProps: Function;
    setClopenState: any;
}

// use Component so it re-renders everytime: `nodes` are not a primitive type
// and therefore aren't included in shallow prop comparison
export class TreeExample extends React.Component<ITreeExampleState> {
    public state: ITreeExampleState = {
        selected: this.props.selected,
        nodes: this.props.nodes,
        n_updates: this.props.n_updates,
        setProps: this.props.setProps,
        setClopenState: this.props.setClopenState
    };

    componentDidUpdate(prevProps) {
        if (prevProps.nodes !== this.props.nodes) {
            this.setState(prevState => ({...prevState, nodes: this.props.nodes}));
        }
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
        const MAX_NUM_OF_SELECTIONS = 1;

        const originallySelected = nodeData.isSelected;
        if (nodeData.hasCaret) {
            if (nodeData.isExpanded) this.handleNodeCollapse(nodeData);
            else this.handleNodeExpand(nodeData);
            return;
        }

        nodeData.isSelected = originallySelected == null ? true : !originallySelected;

        if (nodeData.isSelected) {
            this.state.selected.push(nodeData.fieldId);
        } else {
            const index = this.state.selected.indexOf(nodeData.fieldId);
            if (index > -1) {
                this.state.selected.splice(index, 1);
            }
        }

        // If the number of selected items exceeds that of the max, 
        // reset the selected items and only include the one newly selected
        if (this.state.selected.length > MAX_NUM_OF_SELECTIONS) {
            this.forEachNode(this.state.nodes, n => (n.isSelected = false));
            this.state.selected = [nodeData.fieldId];
            nodeData.isSelected = true;
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

    private forEachNode(nodes: IHierachyTreeNode[], callback: (node: IHierachyTreeNode) => void) {
        if (nodes == null) {
            return;
        }

        // @ts-ignore
        for (const node of nodes) {
            callback(node);
            this.forEachNode(node.childNodes, callback);
        }
    }
}