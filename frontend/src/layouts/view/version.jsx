import { Component } from 'react';
import { host } from '../../utils/utils.js';

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