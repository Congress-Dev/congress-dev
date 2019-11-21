import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';
import ReactDOM from 'react-dom';
import Section from '../nav/sectionbutton.jsx';
import ViewportSection from './viewportsection.jsx';
import PropTypes from 'prop-types';
import { host } from '../common/utils';

class VersionView extends Component {
  constructor(props) {
    super(props);
    fetch(`${host}/versions`)
    .then((res) => {
      return res.json();
    })
    .then((result) => {
      this.setState({versions: result});
    })
  }
  render(){
    return null;
  }
}

export default VersionView;