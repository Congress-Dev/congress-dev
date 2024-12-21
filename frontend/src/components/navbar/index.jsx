import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import {
    Alignment,
    Button,
    Classes,
    Navbar,
    NavbarDivider,
    NavbarGroup,
    NavbarHeading,
} from "@blueprintjs/core";

function NavBar() {
    const history = useHistory();
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedTheme = localStorage.getItem("dark-mode");
        return savedTheme ? JSON.parse(savedTheme) : false;
    });

    const toggleDarkMode = () => {
        setIsDarkMode((prevState) => {
            const newState = !prevState;
            localStorage.setItem("dark-mode", JSON.stringify(newState));
            return newState;
        });
    };

    useEffect(() => {
        if (isDarkMode) {
            window.root.classList.add("bp5-dark");
        } else {
            window.root.classList.remove("bp5-dark");
        }
    }, [isDarkMode]);

    return (
        <Navbar className="main-navbar">
            <NavbarGroup className="main-navbar-group" align={Alignment.LEFT}>
                <NavbarHeading>Congress.Dev</NavbarHeading>
                <NavbarDivider />
                <Button
                    className={Classes.MINIMAL}
                    icon="home"
                    text="Home"
                    onClick={() => {
                        history.push("/home");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="book"
                    text="USCode"
                    onClick={() => {
                        history.push("/uscode");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="th-list"
                    text="Bills"
                    onClick={() => {
                        history.push("/bills");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="people"
                    text="About Us"
                    onClick={() => {
                        history.push("/about");
                    }}
                />
                <Button
                    className={Classes.MINIMAL + " button-right"}
                    icon={isDarkMode ? "flash" : "moon"}
                    onClick={toggleDarkMode}
                />
            </NavbarGroup>
        </Navbar>
    );
}

export default NavBar;
