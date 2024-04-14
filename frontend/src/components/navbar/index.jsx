import React from "react";
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

  return (
    <Navbar className="main-navbar">
      <NavbarGroup align={Alignment.LEFT}>
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
        <Button
          className={Classes.MINIMAL}
          icon="shop"
          text="Swag Store"
          onClick={() => {
            window.location = "https://github.com/Congress-Dev/congress-dev";
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
          className={Classes.MINIMAL}
          icon="envelope"
          text="Contact"
          onClick={() => {
            history.push("/contact");
          }}
        />
      </NavbarGroup>
    </Navbar>
  );
}

export default NavBar;
