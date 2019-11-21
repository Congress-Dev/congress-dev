import React, { Component } from 'react';
import PropTypes from 'prop-types';

const styles = {
  section: {
    border: '1px solid black',
    cursor: 'pointer'
  },
  bold: {
    fontWeight: 'bold'
  },
  light: {
    fontWeight: 'lighter'
  },
  [true]: {
    backgroundColor: '#cdffd8'
  },
  [' ']: {}
}
class Section extends Component {

  render() {
    return <div
      style={ Object.assign({}, styles.section, styles[this.props.change || ' '])}
      onClick={this.props.handler}>
      <span style={styles.bold}>{ this.props.header}</span>
      <span  style={styles.light}>{this.props.subheader}</span>
      </div>
  }

}

Section.propTypes = {
  header: PropTypes.string,
  subheader: PropTypes.string,
  change: PropTypes.bool
}

export default Section;