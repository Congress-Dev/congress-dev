import React, { useState, useContext } from "react";
import { useHistory } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";

import {
    Alignment,
    Button,
    Classes,
    Dialog,
    Popover,
    Menu,
    MenuItem,
    Drawer,
    Icon,
    Navbar,
    NavbarDivider,
    NavbarGroup,
    NavbarHeading,
    Position,
} from "@blueprintjs/core";

import { LoginContext, ThemeContext } from "context";

function AppBar() {
    const history = useHistory();
    const [isOpen, setIsOpen] = useState(false);
    const { isDarkMode, setDarkMode } = useContext(ThemeContext);
    const { user, handleLogin, handleLogout } = useContext(LoginContext);

    const toggleDarkMode = () => {
        setDarkMode(!isDarkMode);
    };

    function handleOpen() {
        setIsOpen(true);
    }

    function handleClose() {
        setIsOpen(false);
    }

    function navigationItems() {
        return (
            <>
                <Button
                    className={Classes.MINIMAL}
                    icon="home"
                    text="Home"
                    onClick={() => {
                        handleClose();
                        history.push("/home");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="learning"
                    text="Learn"
                    onClick={() => {
                        handleClose();
                        history.push("/learn");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="book"
                    text="U.S. Code"
                    onClick={() => {
                        handleClose();
                        history.push("/uscode");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="th-list"
                    text="Bills"
                    onClick={() => {
                        handleClose();
                        history.push("/bills");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="people"
                    text="Legislators"
                    onClick={() => {
                        handleClose();
                        history.push("/members");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="office"
                    text="Committees"
                    onClick={() => {
                        handleClose();
                        history.push("/committees");
                    }}
                />
                <Button
                    className={Classes.MINIMAL}
                    icon="info-sign"
                    text="About Us"
                    onClick={() => {
                        handleClose();
                        history.push("/about");
                    }}
                />
            </>
        );
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
                <img className="logo" src="/favicon-32x32.png" />
                <NavbarHeading
                    onClick={() => {
                        history.push("/");
                    }}
                >
                    Congress.Dev
                </NavbarHeading>
                <NavbarDivider />
                <div className="desktop-nav">{navigationItems()}</div>
            </NavbarGroup>
            <NavbarGroup className="options-group" align={Alignment.RIGHT}>
                <Button
                    className={Classes.MINIMAL}
                    icon={isDarkMode ? "flash" : "moon"}
                    onClick={toggleDarkMode}
                />
                <Popover
                    content={
                        <Menu>
                            {user != null && (
                                <MenuItem
                                    text="Logout"
                                    onClick={handleLogout}
                                />
                            )}
                            {user == null && (
                                <MenuItem text="Login" onClick={handleLogin} />
                            )}
                        </Menu>
                    }
                    placement="bottom"
                >
                    <Button className={Classes.MINIMAL}>
                        {user != null ? (
                            <img
                                src={`data:image/png;base64, ${user.userImage}`}
                                alt="Profile"
                                style={{
                                    width: "30px",
                                    height: "30px",
                                    borderRadius: "50%",
                                }}
                            />
                        ) : (
                            <Icon icon="user" />
                        )}
                    </Button>
                </Popover>
            </NavbarGroup>

            <Drawer
                isOpen={isOpen}
                className={"mobile-nav " + (isDarkMode ? "bp5-dark" : "")}
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
        </Navbar>
    );
}

export default AppBar;
