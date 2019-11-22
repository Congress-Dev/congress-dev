import React, { Component } from 'react';
import PropTypes from 'prop-types';


class NavBarClass extends Component {
  render() {
    const {version} = this.props;
    const versionLookup = JSON.parse(localStorage.getItem('versions'));
    console.log(version);
    return (
    <div style={{marginBottom: '10px'}}>
      <div>
        Congress.dev{(version && versionLookup[version])? `- ${versionLookup[version].title}` : null} <span className="badge badge-pill badge-info">0.0.5</span>
      </div>
      <div bsStyle='pills'>
      <a eventKey={1} href="/">
        Titles
      </a>
      <a eventKey={2} href="/revisions">
        US Code Revisions
      </a>
    
      <a eventKey={2} href="/bills">
        Bills
      </a>
      <a eventKey={2} href="/bills?incl=enr">
        Enrolled Bills
      </a>
    </div>
    </div>);
  }

}
NavBarClass.propTypes = {
  version: PropTypes.number
}

export default NavBarClass;