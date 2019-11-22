import { Scrollbars } from 'react-custom-scrollbars';
import React, { Component } from 'react';
import { shallowCompare } from '../../utils';
import PropTypes from 'prop-types';
import _ from 'lodash';

const styles = {
    bold: {
        fontWeight: 'bold'
    },
    light: {
        fontWeight: 'lighter'
    },
};


class NestedSideBar extends Component {
    constructor(props) {
        super(props);
        console.log(props);
    }
    shouldComponentUpdate(nextProps, nextState) {
        return shallowCompare(this, nextProps, nextState);
    }
    render() {
        const {items, onClick, style, bsStyle} = this.props;
        let addItems = [];
        items.forEach(element => {
            let {number: chapter_number, name, chapter_id} = element;
            addItems.push({
                ind: 0,
                number: chapter_number,
                name,
                chapter_id
            });
            _.chain(element.sub)
            .uniqBy('section_id')
            .sortBy('section_id')
            .forEach(subElement => {
                let {display, heading, section_id, number: section_number} = subElement;
                addItems.push({
                    ind: 1,
                    chapter_number,
                    section_number ,
                    display,
                    heading,
                    section_id,
                    chapter_id
                });
            })
            .value();
        });
        return (
            <Scrollbars>
                <div style={{}}>
                    {
                    addItems.map((item, ind) => {
                        let add = {
        
                        }
                        if(bsStyle) {
                            add['bsStyle'] = bsStyle;
                        }
                        const indent = 10 * item.ind;
                        const calcStyle = {
                            marginLeft:  `${indent}px`,
                            width: `calc(100% -  ${indent}px)`
                        }
                        return (
                            <div
                                key={ind}
                                onClick={()=>{onClick(item)} }
                                style={calcStyle}
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


NestedSideBar.propTypes = {
    items: PropTypes.array,
    onClick: PropTypes.function,
    style: PropTypes.object,
    bsStyle: PropTypes.string
}
export default NestedSideBar;