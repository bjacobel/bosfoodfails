const baseConfig = {
  SocrataURL: 'https://data.cityofboston.gov/resource/427a-3cn5'
};

const configSwitch = {};

configSwitch.prod = Object.assign(baseConfig, {
  ShowReduxDevTools: false,
  HotReload: false
});

configSwitch.dev = Object.assign(baseConfig, {
  ShowReduxDevTools: true,
  HotReload: false
});

const env = process.env.NODE_ENV === 'prod' ? 'prod' : 'dev';
const config = configSwitch[env];
export default config;
