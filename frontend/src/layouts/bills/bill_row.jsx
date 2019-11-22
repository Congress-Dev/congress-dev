import React, { Component } from 'react';
import { versionToFull } from '../../utils';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom'


const chamberToAbbrv = {
  House: 'H.R',
  Senate: 'S'
};

const typeToAbbr = {
  'BillTypes.Bill': ''
};

const styles = {
  vers: {
    marginLeft: '5px',
    marginRight: '5px',
    textDecoration: 'underline',
    cursor: 'pointer'
  },
  pan: {
    marginBottom: '10px'
  }
}
class BillRow extends Component {
  constructor(props) {
    super(props);
    this.storeName = this.storeName.bind(this);
  }
  storeName(bill, bill_version_id){
    const billPrefix = `${chamberToAbbrv[bill.chamber]}${typeToAbbr[bill.bill_type]}`;
    const storage = window.sessionStorage || {
      getItem: () => null,
      setItem: () => null
    };
    storage.setItem(`bill_${bill_version_id}_title`, `${billPrefix}.${bill.bill_number}`);
  }
  render() {
    const {bill = {}} = this.props;
    const billPrefix = `${chamberToAbbrv[bill.chamber]}${typeToAbbr[bill.bill_type]}`;
    const {versions} = bill;
    return (
      <div style={styles.pan}>
        <div>
          <div md={2}>
            <div><h4>{billPrefix}.{bill.bill_number}</h4></div>
            <div><h5><em>{bill.bill_title}</em></h5></div>
          </div>
          <div md={6}>
            <div style={{marginTop:'10px'}}>
              {
                versions.map(({bill_version, bill_version_id}, ind) => {
                  return (<Link onClick={()=>this.storeName(bill, bill_version_id)} to={`bill/${bill_version_id}`} key={bill_version_id} style={styles.vers}>{versionToFull[bill_version]}</Link>)
                })
              }
            </div>
          </div>
        </div>
      </div>
    )
  }

}

BillRow.propTypes = {
  bill: PropTypes.object
}
export default BillRow;