import React, { Component } from 'react';
import { host } from '../common/utils';
import NavBarClass from '../nav/nav.jsx';
import { Grid, Row, Col } from 'react-bootstrap';


class VersionView extends Component {
  constructor(props) {
    super(props);
    this.state = {};
      fetch(`${host}/versions`)
      .then((res) => {
        return res.json()
      })
      .then((result)=>{
        this.setState({versions: result});
        let versionLookup = {};
        result.forEach((item) => {
          versionLookup[item.version_id] = item;
        });
        localStorage.setItem('versions', JSON.stringify(versionLookup));
      });
  }
  render() {
    const {versions = []} = this.state;
    return (
      <Grid>
        <Row>
          <NavBarClass/>
        </Row>
        {
          versions.map((version) => {
            const {base_id, version_id, title} = version;
            if(base_id !== undefined && version_id !== undefined){
              return (
                <div>
                <a href={`/compare/${base_id}/${version_id}`}>{title}</a>
                </div>
              );
            }
            return null;
          })
        }
      </Grid>)
  }

}


export default VersionView;