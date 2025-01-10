import React, { useContext } from "react";
import { Section, Elevation } from "@blueprintjs/core";

import { LoginContext } from "context";

import UnauthedHome from "./unauthed";
import AuthedHome from "./authed";

function Home() {
    const { user } = useContext(LoginContext);

    return (
        <Section
            className="page home-page"
            elevation={Elevation.ONE}
            title="Welcome to Congress.dev"
            subtitle="Empowering Civic Engagement and Understanding"
        >
            {user != null ? <AuthedHome /> : <UnauthedHome /> }
        </Section>
    );
}

export default Home;
