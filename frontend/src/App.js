import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import NavBar from "./components/navbar";
// Pages
import FrontPage from "./pages/frontpage";
import AboutUs from "./pages/aboutus";
import BillViewer from "./pages/billviewer";
import USCodeRevisionList from "./pages/uscodemain";
import USCodeViewer from "./pages/uscodeviewer";
import BillSearch from "./pages/billsearch";
import MemberViewer from "./pages/members";

import "./styles/common.scss";
import "./App.css";

function App() {
  return (
    <Router>
      <NavBar />
      <Switch>
        <Route
          exact
          path="/bill/:congress/:chamber/:billNumber/:billVersion?/diffs/:uscTitle/:uscSection"
          component={BillViewer}
        />
        <Route
          exact
          path="/bill/:congress/:chamber/:billNumber/:billVersion?/diffs/:uscTitle/:uscSection#:hasher"
          component={BillViewer}
        />
        <Route
          exact
          path="/bill/:congress/:chamber/:billNumber/:billVersion?"
          component={BillViewer}
        />

        <Route exact path="/bills" component={BillSearch} />
        <Route exact path="/about" component={AboutUs} />
        <Route exact path="/uscode" component={USCodeRevisionList} />
        <Route exact path="/member/:bioguideId" component={MemberViewer} />
        <Route
          path="/uscode/:uscReleaseId/:uscTitle?/:uscSection?"
          component={USCodeViewer}
        />
        <Route path={["/", "/home"]} component={FrontPage} />
      </Switch>
    </Router>
  );
}

export default App;
