import "./style.scss"

import React, { Component } from 'react';
import PropTypes from 'prop-types';


class Navigation extends Component {
  render() {
    const {version} = this.props;
    const versionLookup = JSON.parse(localStorage.getItem('versions'));
    let versionTitle = undefined;

    if(version && versionLookup[version]) {
        versionTitle = "- " + versionLookup[version].title;
    }

    return (
        <div id="navigation">
            <div class="brand">
                <h1>Congress.dev{versionTitle}</h1>
                <span>0.0.7</span>
            </div>
            <div class="links">
                <a eventKey={1} href="/">Titles</a>
                <a eventKey={3} href="/bills">Bills</a>
            </div>
        </div>
    );
  }

}

Navigation.propTypes = {
  version: PropTypes.number
}

export default Navigation;