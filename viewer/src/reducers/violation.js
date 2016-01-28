import {
  RECEIVED_VIOLATION,
  REQUEST_VIOLATION,
  REQUEST_VIOLATION_FAILED
} from '../actions/violations';

export default function violation(state = {}, action) {
  switch (action.type) {
  case RECEIVED_VIOLATION:
    return
  case REQUEST_VIOLATION_FAILED:
    return Object.assign(state, {
      loading: false,
      error: action.payload.error
    });
  case REQUEST_VIOLATION:
    return Object.assign(state, {
      loading: true
    });
  default:
    return state;
  }
}
