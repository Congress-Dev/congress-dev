import React, { useContext } from "react";
import { Section, SectionCard } from "@blueprintjs/core";

import { LoginContext } from "context";

import UnauthedHome from "./unauthed";
import AuthedHome from "./authed";

function Home() {
    const { user } = useContext(LoginContext);

    return (
        <Section
            className="page home-page"
            title="Welcome to Congress.dev"
            subtitle="Your Gateway to Understanding Federal Legislation."
        >
            {user != null ? <AuthedHome /> : <UnauthedHome />}
        </Section>
    );
}

export default Home;
