import React, { useState } from "react";
import { useHistory } from "react-router-dom";
import { version } from "../../common/version";
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
    // Check if 'dark-mode' key exists in localStorage
    const savedTheme = localStorage.getItem('dark-mode');
    const newState = savedTheme ? JSON.parse(savedTheme) : false;
    if (newState) {
      window.root.classList.add('bp3-dark');
    } else {
      window.root.classList.remove('bp3-dark');
    }
    return newState;
  });

  // Function to toggle dark mode class on the <html> element
  const toggleDarkMode = () => {
    setIsDarkMode(prevState => {
      const newState = !prevState;
      localStorage.setItem('dark-mode', JSON.stringify(newState));

      if (newState) {
        window.root.classList.add('bp3-dark');
      } else {
        window.root.classList.remove('bp3-dark');
      }

      return newState;
    });
  };

  return (
    <Navbar className="main-navbar">
      <NavbarGroup className="main-navbar-group" align={Alignment.LEFT}>
        <NavbarHeading>Congress.Dev - {version}</NavbarHeading>
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
          icon="th-filtered"
          text="Enrolled Bills"
          onClick={() => {
            history.push("/bills?versions=enr&text=");
          }}
        />
        {/* <Button
          className={Classes.MINIMAL}
          icon="shop"
          text="Swag Store"
          onClick={() => {
            window.location = "https://github.com/Congress-Dev/congress-dev";
          }}
        /> */}
        <Button
          className={Classes.MINIMAL}
          icon="people"
          text="About Us"
          onClick={() => {
            history.push("/about");
          }}
        />
        <Button
          className={Classes.MINIMAL}
          icon="envelope"
          text="Contact"
          onClick={() => {
            history.push("/contact");
          }}
        />
        <Button
          className={Classes.MINIMAL + ' button-right'}
          icon={isDarkMode ? 'flash' : 'moon'}
          // text={isDarkMode ? 'Light Mode' : 'Dark Mode'}
          onClick={toggleDarkMode}
        />
      </NavbarGroup>
    </Navbar>
  );
}


export default NavBar;