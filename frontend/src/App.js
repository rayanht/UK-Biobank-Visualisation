import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { BrowserRouter as Router, Route, Redirect, Switch } from "react-router-dom";
import Navbar from './components/Navbar';
import Box from '@material-ui/core/Box';
import GraphPage from './components/graph';
import Toolbar from '@material-ui/core/Toolbar';
import LandingPage from './components/landing';
import './App.css';

const useStyles = makeStyles((theme) => ({
  root: {
    minHeight: '100vh',
    backgroundColor: '#fcfcfc',
    position: "relative"
  },
  appBar: {
    minHeight: "7vh"
  },
}));

function App() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Router>
      <Navbar />
      <Toolbar className={classes.appBar}/>
      <Box height="93vh">
        <Switch>
          <Route exact path="/" component={LandingPage} />
          <Route exact path="/graph" component={GraphPage} />
          <Redirect to="/graph" /> {/* For invalid URLs, redirect */}
        </Switch>
      </Box>
    </Router>
    </div>
  );
}

export default App;
