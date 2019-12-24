import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import { diffWords } from 'diff';
import { host } from '../common/utils';
import { getVersionContent, getBillContent, getBillContent2, getTitles, getTitleContent, getSectionContent } from '../common/titles.js';
import NestedSideBar from '../common/nestedSidebar.js';
import { Grid, Row, Col } from 'react-bootstrap';
import { Scrollbars } from 'react-custom-scrollbars';
import NavBarClass from '../nav/nav.jsx';
import { ListGroup, ListGroupItem } from 'react-bootstrap';
import ViewportSection from '../view/viewportsection.jsx';
import BillViewportSection from './bill_view.jsx';
import _ from 'lodash';

import SyncLoader from 'react-spinners/SyncLoader';

const styles={
    section:{
      marginLeft: '20px',
      marginBottom:'0px'
    },
    'quoted-block': {
        borderWidth: '1px',
        borderStyle:'solid',
        borderColor:'gray',
        backgroundColor: 'lightgray'
    },
    continue: {
      marginLeft: '20px',
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
const mergeContents = function mergeContents(contents) {
    let childLookup = {};
    let parentLookup = {};
    contents.forEach((item)=>{
        const parent = item.parent || 'Legis';
        parentLookup[item.bill_content_id] = parent;
        if(childLookup[parent] == null){
            childLookup[parent] = [item]
        } else {
            childLookup[parent].push(item)
        }
    });
    Object.keys(childLookup).forEach((key)=>{
        childLookup[key] = childLookup[key].sort((a,b)=>a.order-b.order);
    });
    return {childLookup, parentLookup};
}
const mergeContents2 = function mergeContents2(contents) {
  let obj = {};
  _.sortBy(contents, 'content_id').forEach((item)=>{
    if(!item.ident){
      return;
    }
    let ident = item.ident.split('/');
    let parent = `${ident.slice(0,-1).join('/')}`;
    item.child = [];
    obj[item.ident] = item;
    if(!obj[parent]){
      obj[parent] = {child:[]};
    }
    if(obj[parent].child){
      obj[parent].child = [...obj[parent].child, obj[item.ident]]
    } else {
      obj[parent].child = [obj[item.ident]]
    }
  });
  return obj;
}

class BillReader extends Component {
    constructor(props) {
      super(props);
      const {bill_version_id, chapter = null, section} = this.props.match.params;
      this.state = {bill_version_id, contents: null, childLookup: {}, parentLookup: {}, sections: [], titles: [], loading: {}};
      if(bill_version_id && !chapter){
        getBillContent(bill_version_id)
        .then((result)=>{
        //const {childLookup = {}, parentLookup = {}} = mergeContents(result);
          //this.setState({childLookup, parentLookup, contents: result || null});
        });
        getBillContent2(bill_version_id)
        .then((result)=>{
          this.setState({contents: result.content || null, metadata: result.metadata || null});
        });
      } else if(section) {
        getSectionContent(chapter, section)
        .then((result)=>{
          this.setState({contents: mergeContents2(result)});
        });
      }
      getTitles()
      .then((result) => {
        this.setState({titles: result});
        this.getVersion();
      });
      this.generate_divs = this.generate_divs.bind(this);
      this.getVersion = this.getVersion.bind(this);
      this.sidebarClick = this.sidebarClick.bind(this);
      this.elements = [];
      this.viewportRef = React.createRef();
      this.renderViewport = this.renderViewport.bind(this);
      this.handleResetScroll = this.handleResetScroll.bind(this);
      this.scrollTarget = '';
      const storage = window.sessionStorage || {
        getItem: () => null,
        setItem: () => null
      };
    }
    handleResetScroll() {
      if(this.scrollTarget === ''){
        //this.viewportRef.current.scrollTop = 0;
      }
    }
    sidebarClick(obj) {
      const {bill_version_id} = this.state;
      const {section_number, chapter_number} = obj;
      const {chapter = null, section} = this.props.match.params;
      if(section_number) {
        if(!chapter) {
          this.props.history.push(`/bill/${bill_version_id}/chapter/${chapter_number}/s${section_number}`);
        } else {
          window.history.replaceState({}, null, `/bill/${bill_version_id}/chapter/${chapter_number}/s${section_number}`);
        }
        this.setState({contents: null});
        getSectionContent(chapter_number, section_number)
        .then((result)=>{
          this.setState({contents: mergeContents2(result)});
        });
      }
    }
    getVersion() {
      // console.log('Getting version');
      const {bill_version_id} = this.props.match.params;
      const {titles} = this.state;
      getVersionContent(bill_version_id)
      .then((result) => {
        // console.log('res', result);
        let versions = {};
        let diffSections = {};
        let diffChapters = {};
        result.diffs.forEach((item) => {
          versions[`${item.content_id}`] = item;
          diffSections[`${item.section_id}`] = true;
          diffChapters[`${item.chapter_id}`] = true;
        });
        let intTitles = {};
        let intSections = {};
        let sectionLookup = {};
        Object.keys(diffChapters).forEach((chapterId) => {
          titles.forEach((title) => {
            const {chapter_id, number} = title;
            if(`${chapter_id}` == chapterId){
              title.sub = [];
              intTitles[chapter_id] = title;
              // console.log('Getting', number);
              getTitleContent(number)
              .then((result)=>{
                result.forEach((section) => {
                  //console.log(section.section_id);
                  sectionLookup[section.section_id] = section;
                });
                Object.keys(diffSections).forEach((sectionId) => {
                  // Prefetch
                  if(sectionLookup[sectionId]){
                    // console.log(sectionLookup[sectionId]);
                    getSectionContent(intTitles[sectionLookup[sectionId].chapter_id].number, sectionLookup[sectionId].number);
                    intTitles[sectionLookup[sectionId].chapter_id].sub.push(sectionLookup[sectionId]);
                  }
                });
                const {diffTitles = {}} = this.state;
                this.setState({diffTitles: {...diffTitles, ...intTitles}});

              });
            }
          });
        });
        /*Object.keys(diffChapters).forEach((chapterId) => {
          titles.forEach(({chapter_id, number}) => {
            if(`${chapter_id}` == chapterId){
              console.log(number);
            }
          });
        });*/
        // console.log('diff', diffSections);
        this.setState({loading:false, version: bill_version_id, versions, diffSections, diffChapters, diffMerged: mergeContents2(result.contents || [])});
      });
    }
    renderView({ style, ...props }) {
      const top = 0;
      const viewStyle = {
          padding: 15,
          backgroundColor: `rgb(${Math.round(255 - (top * 255))}, ${Math.round(top * 255)}, ${Math.round(255)})`,
          color: `rgb(${Math.round(255 - (top * 255))}, ${Math.round(255 - (top * 255))}, ${Math.round(255 - (top * 255))})`
      };
      return (
          <div
              className="box"
              style={{ ...style, ...viewStyle }}
              {...props}/>
      );
    }

    renderSideBar() {
      const {diffTitles = {}, loading} = this.state;
      if(loading) {
        return <SyncLoader loading={loading}/>
      }
      if(_.isEmpty(diffTitles)) {
        return (<h4 style={styles.centered}>No Differences Found (yet)</h4>);
      }
      return (<NestedSideBar
                items={Object.values(diffTitles)}
                onClick={this.sidebarClick.bind(this)}
                />
              );
    }
    generate_divs(parent) {
      const {contents, metadata} = this.state;
      const {bill_version_id} = this.props.match.params;
      return (
        <BillViewportSection
          contents={{["Legis"]: contents}}
          ident={"Legis"}
          diff={{}}
          scrollElement={this.viewportRef.current}
          loaded={true}
          baseUrl={`/bill/${bill_version_id}`}
          metadata={metadata}
        />
        )

        const {childLookup = {}, parentLookup= {}} = this.state;
        const items = childLookup[parent] || [];
        if(Object.keys(childLookup).length === 0) {
          return (<h3 style={styles.centered}>No Content Found</h3>);
        }
        if(!items) {
          return null;
        }
        return (<div> {
            items.map((item, ind)=> {
              return (
                <div name={item.bill_content_id} style={ parent=== 'Legis' ? {} : (styles[item.content_type] || styles.section) } key={ind}>
                  <span>
                    <b name={item.bill_content_id}>{item.display} {item.heading}</b>
                    {item.heading ? (<p style={ styles.continue }>{item.content}</p>) : <span>{item.content}</span>}
                  </span>
                    { this.generate_divs(item.bill_content_id)}
                </div>
              );
            })
          }
        </div>)
      }
    renderViewport() {
        const {contents, versions, sections, diffMerged} = this.state;
        const {bill_version_id, chapter, section} = this.props.match.params;
        // console.log(contents);
        if(contents){
          let ct2 = {};
          _.forEach(contents,(value, key) => {
            if(ct2[key]) {
              ct2[key].child = [...ct2[key].child, ...value.child]
            } else {
              ct2[key] = value
            }
          });
          _.forEach(diffMerged, (value, key) => {
            if(value.child.length === 1){
              if(ct2[key]) {
                ct2[key].child = _.uniqBy(_.sortBy([...ct2[key].child, ...value.child], (item)=>parseFloat(`${item.order}.${item.content_id}`)), 'content_id');
              } else {
                ct2[key] = {child: value.child}
              }
            }
          });
          const keys = Object.keys(ct2);
          let shortest = keys[0];
          keys.forEach((key)=>{
            if(key.length < shortest.length){
              shortest = key;
            }
          });
          this.handleResetScroll();
          const versionNumbers = _.chain(ct2).keys().map((item)=>item.split(':')[0]).uniq().sortBy((i)=>parseInt(i)).value();
          return (
                  <ViewportSection
                    contents={{[shortest]: ct2[shortest]}}
                    versionNumbers={versionNumbers}
                    ident={shortest}
                    diff={versions}
                    scrollElement={this.viewportRef.current}
                    loaded={sections !== []}
                    baseUrl={`/bill/${bill_version_id}/chapter/${chapter}`}
                  />
                  )
        }
      }
    render() {
        const {contents} = this.state;
        const {chapter} = this.props.match.params;
        // console.log(mergeContents(contents));
        return (
            <Grid>
            <Row>
              <NavBarClass/>
            </Row>
            <Row>
              <Col lg={3} style={ styles.col_a }>
                {this.renderSideBar()}
              </Col>
              <Col lg={9} style={ styles.col_a } ref={this.viewportRef}>
                { chapter ? this.renderViewport() :
                <>
                  {window.performance.mark('Reader') && null}
                  {this.generate_divs('Legis')}
                  {console.log("Reader", window.performance.now('Reader')) && null}
                </>
                  }
              </Col>
            </Row>
          </Grid>
          )
    }
}
BillReader.propTypes = {
    match: PropTypes.object
}
export default BillReader;