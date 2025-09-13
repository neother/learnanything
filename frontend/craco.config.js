module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        "http": false,
        "https": false,
        "url": false,
        "fs": false,
        "net": false,
        "tls": false,
      };
      return webpackConfig;
    },
  },
};