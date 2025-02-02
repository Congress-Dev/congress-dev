import React from "react";
import { Route, BrowserRouter as Router, Switch } from "react-router-dom";
import { GoogleOAuthProvider } from "@react-oauth/google";

import { AppBar } from "components";
import { LoginProvider, PreferenceProvider, ThemeProvider } from "context";
import {
    AboutUs,
    BillSearch,
    BillViewer,
    Home,
    Learn,
    MemberViewer,
    USCodeRevisionList,
    USCodeViewer,
} from "pages";
import MemberSearch from "pages/member-search";
import "styles/common.scss";

function App() {
    return (
        <GoogleOAuthProvider clientId="426317860763-mn045vovp55l1sufso0n2l36ha3sr9pn.apps.googleusercontent.com">
            <LoginProvider>
                <PreferenceProvider>
                    <ThemeProvider>
                        <Router>
                            <AppBar />
                            <Switch>
                                <Route
                                    exact
                                    path="/bill/:congress/:chamber/:billNumber/:billVersion?"
                                    component={BillViewer}
                                />
                                <Route
                                    exact
                                    path="/bills"
                                    component={BillSearch}
                                />

                                <Route
                                    path="/uscode/:uscReleaseId/:uscTitle?/:uscSection?"
                                    component={USCodeViewer}
                                />
                                <Route
                                    exact
                                    path="/uscode"
                                    component={USCodeRevisionList}
                                />
                                <Route
                                exact
                                    path="/members"
                                    component={MemberSearch}
                                />
                                <Route
                                    exact
                                    path="/member/:bioguideId"
                                    component={MemberViewer}
                                />

                                <Route
                                    exact
                                    path="/learn/:section"
                                    component={Learn}
                                />
                                <Route exact path="/learn" component={Learn} />

                                <Route
                                    exact
                                    path="/about"
                                    component={AboutUs}
                                />            
                                <Route path={["/", "/home"]} component={Home} />
                            </Switch>
                        </Router>
                    </ThemeProvider>
                </PreferenceProvider>
            </LoginProvider>
        </GoogleOAuthProvider>
    );
}

export default App;
