import React from 'react';
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography';
import SplitPane from 'react-split-pane';
import Pane from 'react-split-pane/lib/Pane'

// const useStyles = makeStyles((theme) => ({
//   root: {
//     width: "70%",
//     minHeight: 500
//   },
// }));

function GraphPage(props) {

  // const classes = useStyles();

  return (
    <Box height="100%">
      <SplitPane split="vertical">
        <Pane initialSize="50%" minSize="35%">
          <Typography variant="h4" component="h4">
              <strong>Tree</strong>
            </Typography>
            <Box mt={2}>
              Here will be the tree component
            </Box>
        </Pane>
        <Pane initialSize="50%" minSize="35%">
          <Typography variant="h4" component="h4">
              <strong>Graphs</strong>
            </Typography>
            <Box mt={2}>
              Here will be the graph component
            </Box>
        </Pane>
      </SplitPane>
    </Box>

    // <Box         
    // display="flex" 
    // flexDirection="row-reverse" 
    // justifyContent="center" 
    // alignItems="center"
    // pt={5}>
    //   <Card className={classes.root}>
    //     <CardContent>
    //       <Box mx={5} mt={3}>
    //         <Typography variant="h4" component="h4">
    //           <strong>Graphs</strong>
    //         </Typography>
    //         <Box mt={2}>
    //           Here will be the graph component
    //         </Box>
    //       </Box>
    //     </CardContent>
    //   </Card>
    // </Box>
  );
}

export default GraphPage