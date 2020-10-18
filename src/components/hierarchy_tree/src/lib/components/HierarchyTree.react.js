import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {TreeExample} from "./TreeExample";

export default class HierarchyTree extends Component {

    render() {
        const {id, data, clopenState} = this.props;
        const setClopenState = (id, state) => {
            clopenState[id] = state;
        }
        return (
            <TreeExample id={id} nodes={data} setClopenState={setClopenState}/>
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
     * The clopen state of the nodes in the tree.
     */
    clopenState: PropTypes.any
};
