import "./style.scss"

import React, { Component } from 'react';

import Navigation from "../../components/navigation"


class BillsView extends Component {
  render() { 
    return (
        <div class="layout">
            <Navigation />   

            <div class="sidebar">
                <form class="">
                    Bill search <br/><input type="text" name="searchString"/><input type="submit" value="Search"/>
                    <hr/>
                    Chamber of Origin <br/><input type="checkbox" name="house" id="house" checked=""/><label for="house">House</label><br/><input type="checkbox" name="senate" id="senate" checked=""/><label for="senate">Senate</label><br/>
                    <hr/>
                    Bill Status <br/><input type="checkbox" name="ih" id="ih"/><label for="ih">Introduced in the House</label><br/><input type="checkbox" name="is" id="is"/><label for="is">Introduced in the Senate</label><br/><input type="checkbox" name="rfh" id="rfh"/><label for="rfh">Referred in House</label><br/><input type="checkbox" name="rfs" id="rfs"/><label for="rfs">Referred in Senate</label><br/><input type="checkbox" name="rds" id="rds"/><label for="rds">Received in Senate</label><br/><input type="checkbox" name="rhs" id="rhs"/><label for="rhs">Received in House</label><br/><input type="checkbox" name="rcs" id="rcs"/><label for="rcs">Reference Change Senate</label><br/><input type="checkbox" name="rch" id="rch"/><label for="rch">Reference Change House</label><br/><input type="checkbox" name="rs" id="rs"/><label for="rs">Reported in the Senate</label><br/><input type="checkbox" name="rh" id="rh"/><label for="rh">Reported in the House</label><br/><input type="checkbox" name="pcs" id="pcs"/><label for="pcs">Placed on Calendar Senate</label><br/><input type="checkbox" name="pch" id="pch"/><label for="pch">Placed on Calendar House</label><br/><input type="checkbox" name="cps" id="cps"/><label for="cps">Considered and Passed Senate</label><br/><input type="checkbox" name="cph" id="cph"/><label for="cph">Considered and Passed House</label><br/><input type="checkbox" name="eas" id="eas"/><label for="eas">Engrossed amendment Senate</label><br/><input type="checkbox" name="eah" id="eah"/><label for="eah">Engrossed amendment House</label><br/><input type="checkbox" name="es" id="es"/><label for="es">Engrossed in the Senate</label><br/><input type="checkbox" name="eh" id="eh"/><label for="eh">Engrossed in the House</label><br/><input type="checkbox" name="ras" id="ras"/><label for="ras">Referred w/Amendments Senate</label><br/><input type="checkbox" name="rah" id="rah"/><label for="rah">Referred w/Amendments House</label><br/><input type="checkbox" name="enr" id="enr" checked=""/><label for="enr">Enrolled</label>
                </form>
            </div>

            <div class="content">
                <div class="bill">
                </div>
            </div>
        </div>
    );
  }
}

export default BillsView;