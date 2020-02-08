import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import FrontPage from './pages/frontpage';
import AboutUs from './pages/aboutus';
import ContactUs from './pages/contactus';
import BillViewer from './pages/billviewer';

import logo from './logo.svg';
import 'styles/common.scss';
import './App.css';
import NavBar from './components/navbar';

function App() {
  return (
    <Router>
      <NavBar />
      <Switch>
        <Route path="/bill/:congress/:chamber/:billNumber/:billVersion?" component={BillViewer} />
        <Route exact path='/about' component={AboutUs} />
        <Route exact path='/contact' component={ContactUs} />
        <Route path={['/', '/home']} component={FrontPage} />
      </Switch>
    </Router>
  );
}

export default App;