import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import NavBarClass from './components/nav/nav.jsx';
import ViewContainer from './components/view/view.jsx';
import VersionView from './components/versions/list_view.jsx';
import RevisionView from './components/releases/revision_view.jsx';
import BillView from './components/bills/list_view.jsx';
import BillReader from './components/bills/reader.jsx';
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";


class App extends Component {
  render() {
    return (
      <Router>
        <Switch>
          <Route
            path="/revisions" component={RevisionView}
          />
          <Route
            path="/bills" component={BillView}
          />
          <Route path="/bill/:bill_version_id/chapter/:chapter/s:section" component={BillReader} />
          <Route path="/bill/:bill_version_id" component={BillReader} />

          <Route path="/compare/:base_version/:new_version/" component={ViewContainer} />
          <Route path="/compare/:base_version/:new_version/:chapter/s:section" component={ViewContainer} />
          <Route path="/compare/:base_version/:new_version/:chapter" component={ViewContainer} />

          <Route path="/:version_1/:version_2/chapter/:chapter/s:section" component={ViewContainer} />
          <Route path="/:version_1/:version_2/chapter/:chapter" component={ViewContainer} />
          <Route path="/:version_1/:version_2/" component={ViewContainer} />

          <Route path="/:version_1/chapter/:chapter/s:section" component={ViewContainer} />
          <Route path="/:version_1/chapter/:chapter" component={ViewContainer} />
          <Route path="/:version_1/" component={ViewContainer} />

          <Route path="/chapter/:chapter/s:section" component={ViewContainer} />
          <Route path="/chapter/:chapter" component={ViewContainer} />
          <Route path="/" component={ViewContainer} />


        </Switch>
      </Router>
    );
  }
}

export default App;
