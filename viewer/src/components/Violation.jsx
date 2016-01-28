import React, { Component } from 'react';

export default class Violation extends Component {
  render() {
    const { data } = this.props;

    if (data) {
      return (
        <div>
          <h1>{ data.businessname }</h1>
          <h3>{ data.address }, { data.city }</h3>
          <p>Violated MA { data.violation } ({ data.violdesc }) on { data.violdttm }</p>
          <p>Comments:</p>
          <p>{ data.comments }</p>
        </div>
      );
    }

    return <h3>Loading...</h3>;
  }
}
