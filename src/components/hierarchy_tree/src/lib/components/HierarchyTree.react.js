import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {TreeExample} from "./TreeExample";

export default class HierarchyTree extends Component {
    render() {
        const {id, data, selected, n_updates, setProps} = this.props;
        return (
            <TreeExample id={id} nodes={data} selected={selected} n_updates={n_updates} setProps={setProps} />
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

    selected: PropTypes.arrayOf(PropTypes.number),

    n_updates: PropTypes.number
};
