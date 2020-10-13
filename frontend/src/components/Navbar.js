import React from 'react';
import { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { NavLink } from "react-router-dom";
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import Box from '@material-ui/core/Box';
import MenuIcon from '@material-ui/icons/Menu';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import SwipeableDrawer from '@material-ui/core/SwipeableDrawer';
import BarChartIcon from '@material-ui/icons/BarChart';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  appBar: {
    backgroundColor: '#fefefe',
    boxShadow: '0 3px 5px 2px rgba(200, 200, 200, .3)',
    minHeight: "7vh"
  },
  title: {
    marginRight: 15,
    color: '#333333'
  },
  appBarIcon: {
    marginRight: 8,
  },
  button: {
    margin: theme.spacing(1),
    color: '#7A7A7A'
  },
  activeButton: {
    margin: theme.spacing(1),
    backgroundColor: '#f6f6f6',
    color:'#333333'
  },
  drawer: {
    width: '15em'
  },
  drawerListText: theme.typography.button
}));

export default function Navbar() {
  const classes = useStyles();
  const smMedia = useMediaQuery('(max-width:700px)');
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = (open) => (event) => {
    if (event && event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }

    setDrawerOpen(open);
  };

  return (
    <div className={classes.root}>
      <SwipeableDrawer
        anchor='left'
        open={drawerOpen}
        onClose={toggleDrawer(false)}
        onOpen={toggleDrawer(true)}
      >
        <List className={classes.drawer}>
          <ListItem button key="drawer-cases" component={NavLink} exact to={'/graph'} activeClassName='Mui-selected' onClick={toggleDrawer(false)}>
              <ListItemIcon><BarChartIcon /></ListItemIcon>
              <ListItemText classes={{primary: classes.drawerListText}} primary={'Graph'} />
          </ListItem>
        </List>
      </SwipeableDrawer>
      <AppBar className={classes.appBar} position="fixed">
          <Toolbar>
          <Box display={smMedia ? 'block' : 'none'}>
            <IconButton edge="start" className={classes.menuButton} color="transparent" aria-label="menu" onClick={toggleDrawer(true)}>
              <MenuIcon />
            </IconButton>
          </Box>
          <Box flexGrow={smMedia ? 1 : 0}>
            <Typography variant="h6" className={classes.title}>
              UK BioBank Explorer
            </Typography>
          </Box>
          <Box flexGrow={1} display={ smMedia ? 'none' : 'block' }>
            <Button 
              color="inherit" 
              className={classes.button}
              startIcon={<BarChartIcon />}
              component={NavLink} exact to={'/graph'}
              activeClassName={classes.activeButton}>Graphs</Button>
          </Box>
          </Toolbar>
      </AppBar>
    </div>
  );
}
