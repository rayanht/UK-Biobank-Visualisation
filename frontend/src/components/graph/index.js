import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  root: {
    width: "70%",
    minHeight: 500
  },
}));

function Graph(props) {

  const classes = useStyles();

  return (
    <Box         
    display="flex" 
    flexDirection="row-reverse" 
    justifyContent="center" 
    alignItems="center"
    pt={5}>
      <Card className={classes.root}>
        <CardContent>
          <Box mx={5} mt={3}>
            <Typography variant="h4" component="h4">
              <strong>Graphs</strong>
            </Typography>
            <Box mt={2}>
              Here will be the graph component
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Graph