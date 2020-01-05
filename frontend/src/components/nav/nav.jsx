import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Link, Switch } from "react-router-dom";
import { Navbar, Nav, NavItem, NavDropdown, MenuItem } from "react-bootstrap";
import PropTypes from 'prop-types';


class NavBarClass extends Component {
  render() {
    const {version} = this.props;
    const versionLookup = JSON.parse(localStorage.getItem('versions'));
    console.log(version);
    return (
    <Navbar style={{marginBottom: '10px'}}>
      <Navbar.Brand>
        Congress.dev{(version && versionLookup[version])? `- ${versionLookup[version].title}` : null} <span className="badge badge-pill badge-info">0.0.7</span>
      </Navbar.Brand>
      <Nav bsStyle='pills'>
      <NavItem eventKey={1} href="/">
        Titles
      </NavItem>
      <NavItem eventKey={2} href="/revisions">
        US Code Revisions
      </NavItem>

      <NavItem eventKey={2} href="/bills">
        Bills
      </NavItem>
      <NavItem eventKey={2} href="/bills?incl=enr">
        Enrolled Bills
      </NavItem>
    </Nav>
    </Navbar>);
  }

}
NavBarClass.propTypes = {
  version: PropTypes.number
}

export default NavBarClass;