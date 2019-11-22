import _ from 'lodash';
import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import { diffWords } from 'diff';


const styles={
  section:{
    marginLeft: '20px',
    marginBottom:'10px'
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
  scrollbarAdded: {
    backgroundColor: '#2cbe4e',
    width: '50%',
    left: '0px',
    //float: 'left',
    position: 'absolute',
    height: '10px',
    cursor: 'pointer'
  },
  scrollbarRemoved: {
    backgroundColor: '#cb2431',
    width: '50%',
    right: '0px',
    //float: 'right',
    position: 'absolute',
    height: '10px',
    cursor: 'pointer'
  },
  track: {
    position: 'absolute',
    width: '20px',
    right: '-2px',
    bottom: '2px',
    top: '2px'
  }
}

class ViewportSection extends Component {
  constructor(props){
    super(props);
    console.log(props);
    this.elements = [];
    this.elementsSorted = [];
    this.compute_diff = this.compute_diff.bind(this);
    this.diff_style = this.diff_style.bind(this);
    this.handle_scroll = this.handle_scroll.bind(this);
    this.handle_header_click = this.handle_header_click.bind(this);
    this.set_pathname = this.set_pathname.bind(this);
    this.mounted = false;
    this.renderView = this.renderView.bind(this);
    this.scrollRef = React.createRef();
    this.addedNodes = [];
    this.removedNodes = [];
    this.scrollHeight = 1;
    let path = window.location.pathname.split('/');
    this.handleGutterClick = this.handleGutterClick.bind(this);
    this.state = {viewRef: this.props.viewRef, scrollHeight: 1, addedNodes: [], removedNodes: [], scrollTarget: path.splice(props.baseUrl.split('/').length).join('/')};
  }
  handleGutterClick(height) {
    this.scrollRef.current.scrollTop(height);
  }
  handle_header_click(e){
    const target = e.target;
    const name = target.getAttribute('name');
    if(name) {
      this.set_pathname(name);
    }
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
  handle_scroll(e){
    const {scroll} = this.props;
    if(!this.mounted || scroll === false){
      return;
    }
    let picked = '';
    let lastPicked = null;
    for(let ind in this.elementsSorted) {
      let elem  = this.elementsSorted[ind];
      if(elem) {
        lastPicked = picked;
        picked = elem.name;
      }
      if(elem && elem.offset >= e.target.scrollTop) {
        break;
      }
    }
    this.set_pathname(lastPicked || picked);
  }
  diff_style(diff_list) {
    return (
      diff_list.map((part, ind)=>{
        let style = 'unchanged';
        if(part.removed) {
          style = 'removed';
        }else if(part.added) {
          style = 'added';
        }
        return (<span className={style} style={styles[style]} key={ind} > {part.value}</span>)
      })
    );
  }
  compute_diff(item) {
    const {diff = {}} = this.props;
    let newItem = Object.assign({}, item);
    const itemDiff = diff[`${item.content_id}`];
    if(itemDiff){
      ['heading', 'display', 'content'].forEach((key) => {
        if((itemDiff[key] !== undefined) && itemDiff[key] !== item[key]) {
          newItem[key] = this.diff_style(diffWords(item[key] || '', itemDiff[key] || ''));
        }
      })
    }
    return newItem;
  }
  componentWillMount() {
    window.performance.mark('App')
  }
  componentDidMount(){
    console.log(window.performance.now('App'))
    const {viewRef, scrollElement} = this.props;
    const {scrollTarget} = this.state;
    console.log('Scroll target', scrollTarget);
    this.setState({
      viewRef
    });
    let lookupMap = {};
    let height = 0;
    this.elementsSorted = this.elements.map((element) => {
      lookupMap[element.getAttribute('name')] = element.offsetTop;
      height = Math.max(height, element.offsetTop);
      return {offset: element.offsetTop, name: element.getAttribute('name')};
    });
    this.elementsSorted.sort((a,b) => {return a.offset - b.offset});
    console.log(this.scrollRef);
    //if(scrollTarget && scrollTarget !== '' && lookupMap[scrollTarget]){
    //  this.scrollRef.current.scrollTop(lookupMap[scrollTarget]);
    //}
    const addedNodes = ReactDOM.findDOMNode(this).getElementsByClassName('added');
    const removedNodes = ReactDOM.findDOMNode(this).getElementsByClassName('removed');
    const scrollHeight = height;
    this.setState({addedNodes, removedNodes, scrollHeight});
    //console.log(addedNodes, removedNodes);
    //console.log(height, 'pixels');
    //console.log(this.scrollRef.current.trackVertical);
    // ReactDOM.render(<div>test</div>, this.scrollRef.current.trackVertical);
    // ReactDOM.findDOMNode(this.scrollRef.current.trackVertical).appendChild(ReactDOM.div());
    this.mounted = true;
  }

  generate_divs(parent) {
    console.log(parent.ident);
    console.log(parent.child);
    return _.map(parent.child, (raw_item) => {
      const item = this.compute_diff(raw_item);
      // console.log(item);
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
      if(item.ident == '/us/usc/t52/s10305/a/2/B'){
        console.log(raw_item, content, heading)
      }
      if(!item.ident){
        return null;
      }
      return (
        <div name={item.ident.split('/').splice(4).join('/')} style={ styles.section } ref={(elem)=> {this.elements.push(elem)}}>
          <span>
            <b name={item.ident.split('/').splice(4).join('/')} ident={item.ident} onClick={this.handle_header_click}>{item.display}</b> {heading}
            {content && content != heading ? (<p style={ styles.continue }>{content}</p>) : null}
          </span>
          <div style={styles.continue}>
            { this.generate_divs(raw_item)}
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
    const {contents, ident, diff} = this.props;
    const {removedNodes, addedNodes, scrollHeight} = this.state;
    const items = contents[ident];
    if(!items) {
      return null;
    }
    return (
      <span>
      <div
      onScroll={this.handle_scroll}
      ref={this.scrollRef}>
        {this.generate_divs(items)}

      </div>
      <div style={styles.track}>
        { _.map(removedNodes, (elem, ind) => {
          return <div key={ind} onClick={()=>{this.handleGutterClick(elem.offsetTop)}} style={{...styles.scrollbarRemoved, top: `${100*(elem.offsetTop/scrollHeight)}%`}}/>
        })}
        { _.map(addedNodes, (elem, ind) => {
          return <div key={ind} onClick={()=>{this.handleGutterClick(elem.offsetTop)}} style={{...styles.scrollbarAdded, top: `${100*(elem.offsetTop/scrollHeight)}%`}}/>
        })}
      </div>
      </span>
      );
  }
}
ViewportSection.propTypes = {
  contents: PropTypes.object,
  ident: PropTypes.string,
  diff: PropTypes.object,
  scrollElement: PropTypes.any,
  loaded: PropTypes.bool,
  baseUrl: PropTypes.string
}
export default ViewportSection;