import React, { Component } from "react";
import PropTypes from "prop-types";


class ParallexComponent extends Component {
    static propTypes = {
        parallaxController: PropTypes.object,
    };

    constructor(props) {
        super(props)

        this.state = {
            speed: this.props.attributes.speed || 1,

            width: "100%",
            height: this.props.attributes.height || "100%",

            top: this.props.attributes.top || "0%",
            left: this.props.attributes.left,
            right: this.props.attributes.right,

            position: "absolute",
            zIndex: this.props.attributes.zIndex|| "0",

            // background properties
            backgroundRepeat: "no-repeat",
            backgroundPosition: "center",
            backgroundColor: this.props.attributes.backgroundColor || null,
            backgroundImage: (this.props.attributes.src) ? `url(${this.props.attributes.src})` : null,
            backgroundSize: 'cover'
        }

        this.handleScroll = this.throttle(this.handleScroll.bind(this), 20);

        // convert top to px value
        this.top = this.getTop();
    }

    throttle = (fn, wait) => {
        // wait in milliseconds
        let time = Date.now() 

        return function() {
            if ((time + wait - Date.now() < 0)) {
                fn();
                time = Date.now();
            }
        }
    }

    componentDidMount() {
        window.addEventListener('scroll', this.handleScroll);
    }

    componentWillUnmount() {
        window.removeEventListener('scroll', this.handleScroll);
    }

    getTop = () => {
        // var top = this.props.top;
        const top = this.props.attributes.top;
        // if top is in %, turn into px by multiplying against innerHeight
        // otherwise convert to int
        return top.indexOf('%') > 0 ? 
                window.innerHeight * (top.replace('%', '') / 100) :
                parseInt(top, 10);
    }

    handleScroll = () => {
        const speed = this.state.speed;
        const top = this.top;

        // calculate new top
        const pageTop = window.scrollY;
        const newTop = top - (pageTop * speed);

        // set new top position
        this.refs.parallaxElement.style.top = `${newTop}px`;
    }
 
    render() {
        return (
            <div 
                ref="parallaxElement"
                style={{...this.state}}
            >
                {this.props.children}
            </div>
        )
    }
}

export default ParallexComponent;