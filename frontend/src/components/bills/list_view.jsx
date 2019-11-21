import React, { Component } from 'react';
import { host, shallowCompare, versionToFull } from '../common/utils';
import NavBarClass from '../nav/nav.jsx';
import { Grid, Row, Col, Form, Label, FormControl as Control, Checkbox } from 'react-bootstrap';
import _ from 'lodash';
import BillRow from './bill_row.jsx';
import queryString from 'query-string'


const styles = {
  'col': {
    height:'90vh',
    overflowY: 'scroll',
    overflowX: 'hidden'
  },
  'centered': {
    textAlign: 'center'
  },
  'label': {
    'verticalAlign': 'top'
  }
}


class BillRowHolder extends Component {
  constructor(props) {
    super(props);
  }
  shouldComponentUpdate(nextProps, nextState) {
    return shallowCompare(this, nextProps, nextState);
  }
  render() {
    const {filteredBills = []} = this.props;
    let bill_values = Object.values(filteredBills);
    bill_values = bill_values.sort((a,b) => {
      return a.bill_number - b.bill_number;
    });
    return <div>
        { bill_values.length > 0 ?
          bill_values.map((bill) => {
            return <BillRow
              key={bill.bill_id}
              bill={bill}
            />
          }) : <h3 style={styles.centered}>No Bills Found</h3>
        }
    </div>
  }
}
class SearchConfig extends Component {
  constructor(props) {
    super(props);
    this.state = {
      chamber: props.chamber || {house: 1, senate: 1},
      searchString:props.searchString || '',
      statuses: props.statuses || _.mapValues(versionToFull, (o, b) => 1)
    };
    this.handle_uncheck = this.handle_uncheck.bind(this);
    this.handle_uncheck_statuses = this.handle_uncheck_statuses.bind(this);
    this.handle_text = this.handle_text.bind(this);
  }
  handle_uncheck(e){
    const name = e.target.getAttribute('name');
    const {chamber} = this.state;
    chamber[name] = 0 + !chamber[name];
    this.setState({chamber});
  }
  handle_uncheck_statuses(e){
    const name = e.target.getAttribute('name');
    const {statuses} = this.state;
    statuses[name] = 0 + !statuses[name];
    this.setState({statuses});
  }
  handle_text(e){
    this.setState({searchString: e.target.value});
  }
  render(){
    const {chamber, statuses} = this.state;
    console.log(statuses);
    return(
      <Form>
        Bill search <br/>
        <input type="text" name="searchString" onChange={this.handle_text}/>
        <input type="submit" value="Search" onClick={(e)=> {
          e.preventDefault();
          this.props.requestCallback(this.state)
        }}/>
        <hr/>
        Chamber of Origin <br/>
        <input type="checkbox" name="house" id="house" checked={chamber.house} onChange={this.handle_uncheck}/>
        <label htmlFor="house" style={styles.label}>House</label><br/>
        <input type="checkbox" name="senate" id="senate" checked={chamber.senate} onChange={this.handle_uncheck}/>
        <label htmlFor="senate" style={styles.label}>Senate</label><br/>
        <hr/>
        Bill Status <br/>
        {
          _.map(_.keys(statuses), (key, ind) => {
            
            const value = versionToFull[key];
            return (
              <>
                <input type="checkbox" name={key} id={key} checked={statuses[key]} onChange={this.handle_uncheck_statuses}/>
                <label htmlFor={key} style={styles.label}>{value}</label><br/>
              </> )
          })
        }
      </Form>
    )
  }
}


class BillView extends Component {
  constructor(props) {
    super(props);
    let params = queryString.parse(this.props.location.search);
    let statuses = statuses =  _.mapValues(versionToFull, (o, b) => 1);
    if(params.incl){
      statuses =  _.mapValues(versionToFull, (o, b) => 0);
      _.forEach(params.incl.split(','), (v) => {
        statuses[v] = 1;
      });
    }
    if(params.decl){
      _.forEach(params.incl.split(','), (v) => {
        statuses[v] = 0;
      });
    }
    console.log(params);
    if(params.h){
      params.h = parseInt(params.h);
    } else{
      params.h = 1
    }
    if(params.s){
      params.s = parseInt(params.s);
    } else{
      params.s = 1
    }
    if(!params.q){
      params.q = '';
    }
    this.state = {chamber: {house: params.h, senate: params.s}, searchString: params.q, statuses};
    this.formState = {};
    this.handle_text = this.handle_text.bind(this);
    this.make_request = this.make_request.bind(this);
    this.make_request(this.state);
  }
  make_request({chamber, statuses, searchString}) {
    console.log(chamber);
    const incl = _.reduce(_.keys(statuses), (memo, cur) => {
      if(statuses[cur]) {
        return [...memo, cur];
      }
      return memo;
    }, []);
    const decl = _.reduce(_.keys(statuses), (memo, cur) => {
      if(!statuses[cur]) {
        return [...memo, cur];
      }
      return memo;
    }, []);
    let addl = '';
    if(decl.length > 0){
      if(incl.length > decl.length) {
        addl = `&decl=${decl}`;
      }else{
        addl = `&incl=${incl}`;
      }
    }
    window.history.replaceState({}, null, `/bills?s=${chamber.senate}&h=${chamber.house}&q=${searchString}${addl}`);
    fetch(`${host}/bills?s=${chamber.senate}&h=${chamber.house}&q=${searchString}${addl}`)
    .then((res) => {
      return res.json()
    })
    .then((result)=>{
      this.setState({filteredBills: result});
    });
  }
  handle_text(e){
    let {searchString} = this.state;
    searchString = e.target.value;
    this.setState({searchString});
  }
  shouldComponentUpdate(nextProps, nextState) {
    return shallowCompare(this, nextProps, nextState);
  }
  render() {
    const {filteredBills = [], chamber, statuses, searchString} = this.state;
    let bill_values = Object.values(filteredBills);
    bill_values = bill_values.sort((a,b) => {
      return a.bill_number - b.bill_number;
    });
    return (
      <Grid>
        <Row>
          <NavBarClass/>
        </Row>
        <Row>
          <Col md={3}>
            <SearchConfig
              requestCallback={this.make_request}
              statuses = {statuses}
              chamber = {chamber}
              searchString = {searchString}
            />
          </Col>
          <Col md={9} style={styles.col}>
            <BillRowHolder
              filteredBills={filteredBills}
              />
          </Col>
        </Row>
      </Grid>)
  }

}


export default BillView;