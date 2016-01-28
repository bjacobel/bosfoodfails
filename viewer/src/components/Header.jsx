import React, { Component } from 'react';

export default class Header extends Component {
  render() {
    return (
      <div className="header">
        <div className="logo-img"></div>
        <div className="logo-name">
          <a href="https://twitter.com/bosfoodfails">@bosfoodfails </a>
          Citation Inspector
        </div>
      </div>
    );
  }
}
