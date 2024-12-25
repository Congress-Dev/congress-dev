import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import {
    Alignment,
    Button,
    Classes,
    Drawer,
    Navbar,
    NavbarDivider,
    NavbarGroup,
    NavbarHeading,
    Position,
} from "@blueprintjs/core";

function AppBar() {
    const history = useHistory();
    const [isOpen, setIsOpen] = useState(false);

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

    function handleOpen() {
        setIsOpen(true);
    }

    function handleClose() {
        setIsOpen(false);
    }

    function navigationItems() {
        return <>
            <Button
                className={Classes.MINIMAL}
                icon="home"
                text="Home"
                onClick={() => {
                    handleClose()
                    history.push("/home");
                }}
            />
            <Button
                className={Classes.MINIMAL}
                icon="book"
                text="USCode"
                onClick={() => {
                    handleClose()
                    history.push("/uscode");
                }}
            />
            <Button
                className={Classes.MINIMAL}
                icon="th-list"
                text="Bills"
                onClick={() => {
                    handleClose()
                    history.push("/bills");
                }}
            />
            <Button
                className={Classes.MINIMAL}
                icon="people"
                text="About Us"
                onClick={() => {
                    handleClose()
                    history.push("/about");
                }}
            />
        </>
    }

    return (
        <Navbar className="main-navbar">
            <NavbarGroup className="main-navbar-group" align={Alignment.LEFT}>
                <Button
                    className={Classes.MINIMAL + " button-right mobile-drawer"}
                    icon="menu"
                    onClick={() => {
                        handleOpen();
                    }}
                />
                <NavbarHeading>Congress.Dev</NavbarHeading>
                <NavbarDivider />
                <div class="desktop-nav">
                    {navigationItems()}
                </div>

                <Button
                    className={Classes.MINIMAL + " button-right"}
                    icon={isDarkMode ? "flash" : "moon"}
                    onClick={toggleDarkMode}
                />

                <Drawer
                    isOpen={isOpen}
                    className={isDarkMode ? 'bp5-dark' : ''}
                    onClose={handleClose}
                    position={Position.LEFT}
                    canOutsideClickClose={true}
                    autoFocus={true}
                    canEscapeKeyClose={true}
                    enforceFocus={true}
                    hasBackdrop={true}
                    usePortal={true}
                >
                    {navigationItems()}
                </Drawer>
            </NavbarGroup>
        </Navbar>
    );
}

export default AppBar;
