import "./style.scss"

import React, { Component } from 'react';

import Navigation from "../../components/navigation"


class HomeView extends Component {
  render() { 
    return (
        <div class="layout">
            <Navigation />   

            <div class="sidebar">
                &nbsp;
            </div>

            <div class="content">
                <h2>Welcome</h2>
                <p>I started this project to help myself understand what changes our elected officials were proposing to make to our current laws.</p>
                <p>One of the problems with federal legislation is how difficult it is to understand.
                    Federal bills are written as 'instructions to change the current law', and unless you have both the existing law and the bill side by side.
                    these modifications of the bills can very difficult to understand, especially on longer bills. Problems inspire progress and innovation and in that spirit this problem inspired me to create this solution.
                    My course of action was to parse each bill and use semantic clues within the bill's text to determine how the proposed changes affect the current law.
                    I currently display the highlighted changes in a Github-esque fashion to illustrate where they exist.</p>
                <p>It is nowhere near done, unfortunately I am not much of a frontend developer, so I apologize for the state of the site.</p>
                <p>I welcome any and all feedback at: <address><a href="mailto:feedback@congress.dev">feedback@congress.dev</a></address></p>
            </div>
        </div>
    );
  }
}

export default HomeView;
