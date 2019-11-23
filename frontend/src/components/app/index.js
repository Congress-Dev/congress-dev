import "./style.scss"

import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import HomeView from "../../layouts/home"
import BillsView from "../../layouts/bills"

import Navigation from "../../components/navigation"


class Blank extends Component {
  render() { 
    return (
      <div>
          <Navigation />    
      </div>
    );
  }
}


class App extends Component {

  render() {
    return (
      <Router>
        <Switch>
          <Route path="/revisions" component={ Blank } />

          <Route path="/bills" component={ BillsView } />
          <Route path="/bill/:bill_version_id/chapter/:chapter/s:section" component={ BillsView } />
          <Route path="/bill/:bill_version_id" component={ BillsView } />

          <Route path="/compare/:base_version/:new_version/" component={ Blank } />
          <Route path="/compare/:base_version/:new_version/:chapter/s:section" component={ Blank } />
          <Route path="/compare/:base_version/:new_version/:chapter" component={ Blank } />

          <Route path="/:version_1/:version_2/chapter/:chapter/s:section" component={ Blank } />
          <Route path="/:version_1/:version_2/chapter/:chapter" component={ Blank } />
          <Route path="/:version_1/:version_2/" component={ Blank } />

          <Route path="/:version_1/chapter/:chapter/s:section" component={ Blank } />
          <Route path="/:version_1/chapter/:chapter" component={ Blank } />
          <Route path="/:version_1/" component={ Blank } />

          <Route path="/chapter/:chapter/s:section" component={ Blank } />
          <Route path="/chapter/:chapter" component={ Blank } />
          
          <Route path="/" component={ HomeView } />
        </Switch>
      </Router>
    );
  }

}

export default App;
