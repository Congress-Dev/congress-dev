import _ from 'lodash';
import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { versionToFull, chamberToShort } from '../../utils/utils.js';


const bgStyles = {
  [true]: {
    backgroundColor: 'rgba(205, 255, 216, 0.50)'
  },
  [false]:{
    // backgroundColor: 'rgba(255, 220, 224, 0.50)'
  },
  nothing: {}
};
const styles={
    section:{
      marginLeft: '10px',
      marginBottom:'0px',
    },
    'quoted-block': {
        borderWidth: '1px',
        borderStyle:'solid',
        borderColor:'gray',
        backgroundColor: 'lightgray'
    },
    continue: {
      marginLeft: '22px',
      marginBottom: '0px'
    },
    unchanged: {},

    added: {
      backgroundColor: '#cdffd8'
    },
    removed: {
      backgroundColor: '#ffdce0',
      textDecoration: 'line-through',
      textDecorationColor: '#FF576B'
    },
    centered: {
      textAlign: 'center'
    },
    font: {
      fontFamily: 'serif',
      textAlign: "justify"
    },
    'col_a': {
      height:'90vh',
      overflowX: 'wrap'
    },
    'col': {
      height:'90vh',
      overflowX: 'wrap'
    },
    'sidebar': {
    }
  }

class BillViewportSection extends Component {
  constructor(props){
    super(props);
    this.elements = [];
    this.elementsSorted = [];
    this.set_pathname = this.set_pathname.bind(this);
    this.mounted = false;
    this.renderView = this.renderView.bind(this);
    this.getbg = this.getbg.bind(this);
    this.addedNodes = [];
    this.removedNodes = [];
    this.scrollHeight = 1;
    let path = window.location.pathname.split('/');
    this.state = {viewRef: this.props.viewRef, scrollHeight: 1, addedNodes: [], removedNodes: [], scrollTarget: path.splice(props.baseUrl.split('/').length).join('/')};
  }
  set_pathname(targetPath) {
    const {baseUrl} = this.props;
    let current = window.location.pathname.split('/');
    current.splice(3);
    let newPath = `${baseUrl}/${targetPath}`;
    if(newPath !== window.location.pathname){
      window.history.replaceState({}, null, newPath);
    }
  }
  getbg(item) {
    const vs = _.values(item);
    if(vs.length == 0){
      return "nothing";
    }
    return vs[0];
  }

  generate_divs(parent) {
    return _.map(parent.child, (item) => {
      let heading = null;
      let content = null;
      if(item.heading) {
        heading = item.heading;
      }
      if(item.content) {
        if(!heading) {
          heading = item.content;
        } else {
          content = item.content;
        }
      }
      const bgStyle = bgStyles[this.getbg(item.ap)];
      return (
        <div key={item.bill_content_id} name={item.bill_content_id} style={ parent=== 'Legis' ? {...styles.font} : (styles[item.content_type] || styles.section) } ref={(elem)=> {this.elements.push(elem)}}>
          <span style={{...bgStyle, ...styles.font}}>
          <b style={styles.font} name={item.bill_content_id}>{item.display} {item.heading}</b>
                    {item.heading ? (<p style={ {...styles.continue, ...bgStyle, ...styles.font} }>{item.content}</p>) : <span>{item.content}</span>}
          </span>
          <div style={{...styles.continue, ...styles.font}}>
            { this.generate_divs(item)}
          </div>
        </div>
      );
    });
  }
  renderView({ style, ...props }) {
    const {addedNodes, removedNodes, scrollHeight} = this.state;
    //console.log(this);
    const top = 0;
    const viewStyle = {
        right: 2,
        bottom: 2,
        top: 2,
        borderRadius: 3
    };
    return (
        <div
            style={{ ...style, ...viewStyle }}
            {...props}
          />
    );
}
  render() {
    const {contents, ident, diff, metadata} = this.props;
    const {removedNodes, addedNodes, scrollHeight} = this.state;
    const items = contents[ident];
    if(!items) {
      return null;
    }
    return (
      <div>
        {
          metadata ? <>
          <h1 style={{...styles.font, ...styles.centered}}>{chamberToShort[metadata.chamber]} {metadata.number}</h1>
          <h3 style={{...styles.font, ...styles.centered, fontStyle: 'italic'}}>{versionToFull[metadata.version]}</h3>
          </>: null}

        {this.generate_divs(items)}
      </div>
      );
  }
}
BillViewportSection.propTypes = {
  contents: PropTypes.object,
  metadata: PropTypes.object,
  ident: PropTypes.string,
  diff: PropTypes.object,
  scrollElement: PropTypes.any,
  loaded: PropTypes.bool,
  baseUrl: PropTypes.string
}
export default BillViewportSection;