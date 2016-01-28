import config from '../constants/config';

import 'isomorphic-fetch';

export const getViolation = (violation) => {
  return fetch(`${config.SocrataURL}/${violation}.json`)
    .then((response) => {
      return response.json();
    })
    .then((viol) => {
      return viol;
    });
};
