import config from './constants/config';
import React from 'react';
import ReactDOM from 'react-dom';
import thunk from 'redux-thunk';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';

import { createDevTools } from 'redux-devtools';
import LogMonitor from 'redux-devtools-log-monitor';
import DockMonitor from 'redux-devtools-dock-monitor';

import './stylesheets';
import reducer from './reducers';
import Main from './components/Main';

const DevTools = createDevTools(
  <DockMonitor toggleVisibilityKey="ctrl-h" changePositionKey="ctrl-q">
    <LogMonitor theme="tomorrow" />
  </DockMonitor>
);

const composedCreateStore = compose(
  applyMiddleware(thunk),
  DevTools.instrument()
)(createStore);

const store = composedCreateStore(reducer);

let devTools;
if (config.ShowReduxDevTools) {
  devTools = <DevTools/>;
}

ReactDOM.render(
  <div>
    <Provider store={ store }>
      <div>
        <Main />
        { devTools }
      </div>
    </Provider>
  </div>,
  document.getElementById('main')
);
