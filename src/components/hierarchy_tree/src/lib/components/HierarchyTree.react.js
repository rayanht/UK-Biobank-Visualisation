import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {TreeExample} from "./TreeExample";

export default class HierarchyTree extends Component {
    render() {
        const {id} = this.props;

        return (
            <TreeExample id={id}/>
        );
    }
}

HierarchyTree.defaultProps = {};

HierarchyTree.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,
};
