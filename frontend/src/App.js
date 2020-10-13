import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { BrowserRouter as Router, Route, Redirect, Switch } from "react-router-dom";
import Navbar from './components/Navbar';
import Box from '@material-ui/core/Box';
import Graph from './components/graph';
import LandingPage from './components/landing';
import './App.css';

const useStyles = makeStyles((theme) => ({
  root: {
    minHeight: '100vh',
    backgroundColor: '#fafafa',
    position: "relative"
  }
}));

function App() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Router>
      <Navbar />
      <Box py={10}>
        <Switch>
          <Route exact path="/" component={LandingPage} />
          <Route exact path="/graph" component={Graph} />
          <Redirect to="/graph" /> {/* For invalid URLs, redirect */}
        </Switch>
      </Box>
    </Router>
    </div>
  );
}

export default App;
