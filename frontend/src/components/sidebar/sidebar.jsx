import { Scrollbars } from 'react-custom-scrollbars';
import React, { Component } from 'react';
import { shallowCompare } from '../../utils/utils.js';
import PropTypes from 'prop-types';


const styles = {
    bold: {
        fontWeight: 'bold'
    },
    light: {
        fontWeight: 'lighter'
    },
};


class SideBar extends Component {
    constructor(props) {
        super(props);
    }
    shouldComponentUpdate(nextProps, nextState) {
        return shallowCompare(this, nextProps, nextState);
    }
    render() {
        const {items, onClick, style, bsStyle} = this.props;
        return (
            <Scrollbars>
                <div style={{}}>
                    {
                    items.map((item, ind) => {
                        let add = {
        
                        }
                        if(bsStyle) {
                            add['bsStyle'] = bsStyle;
                        }
                        return (
                            <div
                                key={ind}
                                onClick={()=>{onClick(item)} }
                                {...add}
                            >
                                <span style={styles.bold}>{item.display || item.number}</span>{' '}
                                <span style={styles.light}>{item.heading || item.name}</span>
                            </div>
                        )
                    
                    })
                }
                
            </div>
        </Scrollbars>
        );
    }
}


SideBar.propTypes = {
    items: PropTypes.array,
    onClick: PropTypes.function,
    style: PropTypes.object,
    bsStyle: PropTypes.string
}
export default SideBar;