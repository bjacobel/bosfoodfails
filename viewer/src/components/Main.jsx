import React, { Component } from 'react';
import { connect } from 'react-redux';

import Header from './Header';
import Violation from './Violation';

import { fetchViolation } from '../actions/violations';

const mapStateToProps = (state) => {
  return {
    violation: state.violation
  };
};

const mapDispatchToProps = {
  fetchViolation
};

class Main extends Component {
  componentWillMount() {
    const { fetchViolation } = this.props;  // eslint-disable-line no-shadow

    fetchViolation();
  }

  render() {
    const { violation } = this.props;

    return (
      <div>
        <Header/>
        <Violation data={ violation }/>
      </div>
    );
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Main);
