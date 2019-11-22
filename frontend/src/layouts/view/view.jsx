import React, { Component } from 'react';
import ViewportSection from './viewportsection.jsx';
import PropTypes from 'prop-types';
import { getTitles, getTitleContent, getSectionContent, getVersionContent, getRevisionDiff } from '../../utils/titles.js';
import SideBar from '../../components/sidebar/sidebar.jsx';
import NavBarClass from '../../components/nav/nav.jsx';
import _ from 'lodash';


const styles = {
  'col_a': {
  },
  'col': {
  },
  'sidebar': {
  },
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

const blurb = (<><h3>Welcome</h3>
  <p>I started this project to help myself understand what changes our elected officials were proposing to make to our current laws.</p>
  <p>One of the problems with federal legislation is how difficult it is to understand.<br />
    Federal bills are written as 'instructions to change the current law', and unless you have both the existing law and the bill side by side.<br />
    these modifications of the bills can very difficult to understand, especially on longer bills. Problems inspire progress and innovation and in that spirit this problem inspired me to create this solution.<br />
    My course of action was to parse each bill and use semantic clues within the bill's text to determine how the proposed changes affect the current law.<br />
    I currently display the highlighted changes in a Github-esque fashion to illustrate where they exist.</p>
  <p>It is nowhere near done, unfortunately I am not much of a frontend developer, so I apologize for the state of the site.</p>
  I welcome any and all feedback at: <address><a href="mailto:feedback@congress.dev">feedback@congress.dev</a></address>
</>);
const mergeContents = function mergeContents(contents) {
  let obj = {};
  console.log(_.sortBy(contents, 'content_id'));
  _.sortBy(contents, 'content_id').forEach((item) => {
    if (!item.ident) {
      return;
    }
    let ident = item.ident.split('/');
    let parent = `${ident.slice(0, -1).join('/')}`;
    item.child = [];
    obj[item.ident] = item;
    if (!obj[parent]) {
      obj[parent] = { child: [] };
    }
    if (obj[parent].child) {
      obj[parent].child = [...obj[parent].child, obj[item.ident]]
    } else {
      obj[parent].child = [obj[item.ident]]
    }
  });
  return obj;
}
class ViewContainer extends Component {

  constructor(props) {
    super(props);
    const { chapter, section, new_version, other, version_1, version_2 } = this.props.match.params;
    console.log(this.props.match.params);
    let scrollOffset = 3;
    let versionPrefix = "";
    if (version_1) {
      scrollOffset += 1;
      versionPrefix = `/${version_1}`;
    }
    if (version_2) {
      scrollOffset += 1;
      versionPrefix = `/${version_1}/${version_2}`;
    }
    let path = window.location.pathname.split('/');
    this.scrollTarget = path.splice(scrollOffset).join('/');
    this.state = { sections: [], version: new_version, versionPrefix };
    if (version_1 && version_2) {
      getRevisionDiff(version_1, version_2)
      .then((result) => {
        console.log(result);
      });
    }
    if (chapter) {
      getTitleContent(chapter)
        .then((result) => {
          const { contents } = this.state;
          this.setState({ sections: result, contents: contents || null, titleId: chapter });
        });
    } else {
      // Fetch the current list of titles
      getTitles()
        .then((result) => {
          // console.log(result);
          this.setState({ 'titles': result });
        })
    }
    if (section) {
      getSectionContent(chapter, section)
        .then((result) => {
          this.setState({ contents: mergeContents(result) });
        });
    }
    if (new_version !== undefined) {

      getVersionContent(new_version)
        .then((result) => {
          let versions = {};
          let diffSections = {};
          let diffChapters = {};
          result.diffs.forEach((item) => {
            versions[`${item.content_id}`] = item;
            diffSections[`${item.section_id}`] = true;
            diffChapters[`${item.chapter_id}`] = true;
          });
          this.setState({ version: new_version, versions, diffSections, diffChapters, versionContents: result.contents });
        });
    }
    this.renderSideBar = this.renderSideBar.bind(this);
    this.renderViewport = this.renderViewport.bind(this);

    this.handleSectionclick = this.handleSectionclick.bind(this);
    this.handleResetScroll = this.handleResetScroll.bind(this);
    this.viewportRef = React.createRef();
  }
  handleResetScroll() {
    if (this.scrollTarget === '') {
      this.viewportRef.current.scrollTop = 0;
    }
  }
  handleSectionclick({ number: sectionId }) {
    const { titleId, versionContents = [], versionPrefix } = this.state;
    let filteredContents = [];

    this.props.history.push(`${versionPrefix}/chapter/${titleId}/s${sectionId}`);
    getSectionContent(titleId, sectionId)
      .then((result) => {
        versionContents.forEach((content) => {
          if (content.section_id === result[0].section_id) {
            filteredContents.push(content);
          }
        });
        this.setState({ contents: mergeContents([...result, ...filteredContents]) });
      });
  }
  handleTitleClick({ number: titleId }) {
    const { versionPrefix } = this.state;
    console.log(arguments);
    console.log(this);
    this.props.history.push(`${versionPrefix}/chapter/${titleId}`);
    getTitleContent(titleId)
      .then((result) => {
        this.setState({ titleId, sections: result, contents: null, titles: null });
      });
  }
  renderSideBar() {
    const { sections, titles, versions, diffSections = {}, diffChapters = {} } = this.state;
    let content = [];
    let onclick = null;
    if (titles) {
      console.log(titles);
      content = titles.filter((item) => {
        return !versions || diffChapters[`${item.chapter_id}`];
      });
      onclick = this.handleTitleClick.bind(this);
    } else if (sections) {
      content = sections.filter((item) => {
        return !versions || diffSections[`${item.section_id}`]
      });
      onclick = this.handleSectionclick.bind(this);
    }
    return (<SideBar
      items={content}
      onClick={onclick}
      style={{}}
      bsStyle={versions ? 'success' : null}
    />
    );
  }
  renderViewport(viewRef) {
    const { contents, versions, sections, titleId, versionPrefix } = this.state;
    if (contents) {
      const keys = Object.keys(contents);
      let shortest = keys[0];
      keys.forEach((key) => {
        if (key.length < shortest.length) {
          shortest = key;
        }
      });
      this.handleResetScroll();
      return (<ViewportSection
        contents={{ [shortest]: contents[shortest] }}
        ident={shortest}
        diff={versions}
        scrollElement={this.viewportRef.current}
        scrollTarget={this.scrollTarget}
        baseUrl={`${versionPrefix}/chapter/${titleId}`}
        loaded={sections !== []}
      />
      )
    } else {
      return (blurb)
    }
  }
  render() {
    const { version } = this.state;
    return (
      <div>
        <div>
          <NavBarClass
            version={version}
          />
        </div>
        <div>
          <div lg={3} style={styles.col_a}>
            {this.renderSideBar()}
          </div>
          <div lg={9} style={styles.col} ref={this.viewportRef}>
            {this.renderViewport()}

          </div>
        </div>
      </div>
    )
  }
}
ViewContainer.propTypes = {
  match: PropTypes.object
}
export default ViewContainer;