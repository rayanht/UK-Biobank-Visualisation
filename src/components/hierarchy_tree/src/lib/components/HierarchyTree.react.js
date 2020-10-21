import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {TreeExample} from "./TreeExample";

export default class HierarchyTree extends Component {

    render() {
        const {id, data, selected_nodes, max_selections, n_updates, setProps, clopenState} = this.props;
        const setClopenState = (id, state) => {
            clopenState[id] = state;
        }
        return (
            <TreeExample id={id} nodes={data} selected_nodes={selected_nodes} max_selections={max_selections}
                         n_updates={n_updates} setProps={setProps} setClopenState={setClopenState}/>
        );
    }
}

HierarchyTree.defaultProps = {};

HierarchyTree.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * The data displayed in the tree.
     */
    data: PropTypes.array,

    /**
     * An array of selected nodes
     */
    selected_nodes: PropTypes.arrayOf(PropTypes.number),

    /**
     * The maximum number of nodes that should be selected at any time
     */
    max_selections: PropTypes.number,

    /**
     * A count of the number of times the inputs have updated, so the callback function knows when to update
     */
    n_updates: PropTypes.number,
    
    /**
     * The clopen state of the nodes in the tree.
     */
    clopenState: PropTypes.any
};
