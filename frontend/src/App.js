import React from "react";
import { Route, BrowserRouter as Router, Switch } from "react-router-dom";

import { AppBar } from "components";
import {
    AboutUs,
    BillSearch,
    BillViewer,
    Home,
    MemberViewer,
    USCodeRevisionList,
    USCodeViewer,
} from "pages";

import "styles/common.scss";

function App() {
    return (
        <Router>
            <AppBar />
            <Switch>
                <Route
                    exact
                    path="/bill/:congress/:chamber/:billNumber/:billVersion?"
                    component={BillViewer}
                />
                <Route exact path="/bills" component={BillSearch} />

                <Route
                    path="/uscode/:uscReleaseId/:uscTitle?/:uscSection?"
                    component={USCodeViewer}
                />
                <Route exact path="/uscode" component={USCodeRevisionList} />

                <Route
                    exact
                    path="/member/:bioguideId"
                    component={MemberViewer}
                />

                <Route exact path="/about" component={AboutUs} />
                <Route path={["/", "/home"]} component={Home} />
            </Switch>
        </Router>
    );
}

export default App;
