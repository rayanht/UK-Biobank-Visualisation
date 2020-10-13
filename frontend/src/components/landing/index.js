import React, { useEffect } from 'react';
import { useState } from 'react';
import ParallaxComponent from '../ParallaxComponent';

export default function Landing() {
    
    const fillerDescription = 
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur at gravida lorem, non pharetra eros. Phasellus nec rutrum nibh. Nulla vel mi lectus. Sed volutpat laoreet eleifend. Aenean et consectetur nisl. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Cras semper ligula vitae turpis commodo luctus eget vel eros. Aliquam erat volutpat. Donec ac vehicula justo. Mauris tortor enim, efficitur sit amet varius pulvinar, ultricies eget mi. Donec consectetur velit eget dui accumsan, nec dignissim massa mattis. Praesent imperdiet mauris quis libero efficitur mollis. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vestibulum nec eros ac elit facilisis eleifend non porta ante."
        +
        "\n\nNulla est neque, rutrum vel eros sollicitudin, commodo maximus dui. Nulla ut augue neque. Maecenas finibus efficitur orci, ac luctus justo finibus ac. Vestibulum pretium neque ac blandit pulvinar. Donec molestie neque tortor, at finibus arcu tristique et. Praesent at sem nisi. Vivamus tempus diam id arcu tincidunt faucibus. Proin porttitor turpis eu elit euismod elementum. In nulla elit, sollicitudin ac nibh vitae, lobortis imperdiet urna. Aliquam pretium, est sit amet vestibulum sollicitudin, metus dolor auctor tortor, nec dictum mi tortor vel nisl. Fusce ac elit pulvinar, tempus ante sed, tincidunt mi. Quisque ut metus vel ante viverra dapibus in eget ipsum. Donec sollicitudin diam turpis, non iaculis sapien tincidunt quis."
        +
        "\n\nVestibulum ac ipsum sollicitudin nulla ullamcorper efficitur vel efficitur eros. Donec sit amet odio vel ex vestibulum pellentesque ut vitae eros. Nunc rhoncus vestibulum feugiat. Mauris vehicula ultrices arcu nec commodo. Etiam sodales orci nec enim vulputate, sed tincidunt ante dictum. Etiam iaculis tincidunt quam, non posuere nisi maximus sit amet. Sed pretium ultricies magna, sit amet suscipit tellus porttitor eu."
        +
        "\n\nVestibulum sed accumsan sem, vitae aliquet nisl. Nullam turpis felis, pharetra in porttitor quis, ullamcorper vel velit. Integer vel imperdiet leo, non cursus elit. Aliquam erat volutpat. Cras ultrices nisl erat, fringilla elementum ex hendrerit ac. In elementum in nisi in condimentum. Maecenas maximus vitae nisi a consectetur. Suspendisse luctus condimentum tincidunt. Maecenas eget elit vehicula, laoreet odio quis, faucibus tellus. Ut nec diam sed enim porttitor vehicula. Mauris vestibulum cursus neque at ultricies. Pellentesque lectus nulla, gravida quis mauris sed, cursus dapibus est. Morbi bibendum tellus in ipsum porta, eu volutpat quam viverra. Maecenas sed neque pretium, tincidunt tortor et, hendrerit lorem. Fusce dignissim sed nibh vel ornare. Quisque vitae volutpat ante, et finibus augue."
        +
        "\n\nMorbi nibh ipsum, tempor in lacus sed, malesuada faucibus odio. Etiam quam odio, pretium tincidunt consectetur vel, semper ac ex. Aenean laoreet nulla eget metus congue, id tristique augue feugiat. Sed tellus dui, eleifend quis tempor quis, interdum id nibh. Nulla luctus vel enim eu commodo. Sed sodales lectus lectus, maximus dictum mauris consectetur id. Praesent eu justo at risus scelerisque volutpat. Nam laoreet massa interdum quam vestibulum, sed suscipit velit elementum. Donec tempus tristique tellus nec tincidunt. Nulla eget pulvinar sem."
    
    const makeWhiteSpace = (paragraph) => {
        return ("" + paragraph).split("\n").map((text, i) => i ? [<br/>, text] : text)
    }

    // initialise description and cover image, using placeholder now
    const description = makeWhiteSpace(fillerDescription);
    const coverImage = require("../../images/coverImage.jpg");

    const getCoverImageDescription = () => { return(
        <div style={{display: "flex", alignItems: "center"}}>
            <p style= {{color: "white",
                    textAlign: "center",
                    fontFamily: "Calibri",
                    fontSize: "30pt",
                    flex: "1"}}> 
            Biobank Data 
            </p>
        </div>
    )}

    const getDescriptionBody = () => { return (
        <div style={{padding:"1% 30%", backgroundColor:"#fff"}}>
            <p 
                // style= {pageTitleStyle}
            > 
                Home 
            </p>
                {description}
        </div>
    )}

    // initialise parallax attributes for cover image and description
    const [parallaxElements, setParallaxElements] = useState(
        [{
            // cover image
            speed: 0.4,
            top: "0%",
            height: "70%",
            zIndex: "0",
            src: coverImage,
            // style: {coverImageStyle}
        }, {
            // words on cover image
            speed: 1.5,
            top: "25%",
            height: "20%",
            backgroundColor: "rgba(0, 0, 0, 0.4)",
            style: {display:"flex"},
            content: getCoverImageDescription()
        }, 
        {
            // description
            speed: 2.5,
            top: "80%",
            height: "400px",
            color: "#fff",
            content: getDescriptionBody()
        }]
    )

    return (
        <div>
            {parallaxElements.map((element, index) => {
                return (element.content) ? 
                (
                    <ParallaxComponent key={index} attributes={element}>
                        {element.content}
                    </ParallaxComponent>
                )
                : 
                (
                    <ParallaxComponent key={index} attributes={element} />
                )
            })}
        </div>
    );
}
