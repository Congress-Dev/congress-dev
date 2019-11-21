import React, { Component } from 'react';
import { host } from '../common/utils';
import NavBarClass from '../nav/nav.jsx';
import { Grid, Row, Col } from 'react-bootstrap';
import lodash from 'lodash';


const styles = {
    [true]: {
        backgroundColor: 'lightblue',
        cursor: 'pointer'
    },
    [false]: { cursor: 'pointer' }
}
class RevisionView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selected_1: null,
            selected_2: null,
        };

        fetch(`${host}/revisions`)
            .then((res) => {
                return res.json();
            })
            .then((result) => {
                console.log(result);
                this.setState({ versions: result });
                let versionLookup = {};
                result.forEach((item) => {
                    versionLookup[item.version_id] = item;
                });
                localStorage.setItem('revisions', JSON.stringify(versionLookup));
            });
        this.handleClickSelect = this.handleClickSelect.bind(this);
        this.handleCompareClick = this.handleCompareClick.bind(this);
    }
    handleClickSelect(version_id) {
        const { selected_1, selected_2 } = this.state;
        if (selected_1 === null) {
            this.setState({ selected_1: version_id });
        } else if (selected_2 === null && selected_1 !== version_id) {
            this.setState({ selected_2: version_id });
        } else if (selected_1 === version_id) {
            this.setState({ selected_1: selected_2, selected_2: null });
        } else if (selected_2 === version_id) {
            this.setState({ selected_2: null });
        }
    }
    handleCompareClick() {
        const { selected_1, selected_2 } = this.state;
        if (selected_1 !== null && selected_2 !== null) {
            window.location = `${selected_1}/${selected_2}/`;
        }
    }
    render() {
        const { versions = [], selected_1, selected_2 } = this.state;
        let lookup = lodash.keyBy(versions, 'version_id');
        lookup[null] = { title: '' };
        const filteredVersions = lodash.filter(versions, (x) => { return selected_1 === null || x.version_id >= selected_1 });
        return (
            <Grid>
                <Row>
                    <NavBarClass />
                </Row>
                <div>
                    <button onClick={this.handleCompareClick} type='button'>Compare</button> {lookup[selected_1].title} with {lookup[selected_2].title}
                </div>
                {
                    filteredVersions.map((version) => {
                        const { base_id, version_id, title } = version;
                        const itemStyle = styles[version_id === selected_1 || version_id === selected_2];
                        console.log(itemStyle);
                        if (base_id === undefined && version_id !== undefined) {
                            return (
                                <div key={version.version_id}>
                                    <a style={itemStyle} onClick={() => this.handleClickSelect(version_id)}>{title}</a>
                                </div>
                            );
                        }
                        return null;
                    })
                }
            </Grid>)
    }

}


export default RevisionView;