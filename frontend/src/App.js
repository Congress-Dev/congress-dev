import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import NavBar from "components/navbar";
import {
    AboutUs,
    FrontPage,
    BillViewer,
    USCodeRevisionList,
    USCodeViewer,
    BillSearch,
    MemberViewer,
} from "pages";

import "styles/common.scss";

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
                <Route
                    exact
                    path="/member/:bioguideId"
                    component={MemberViewer}
                />
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
