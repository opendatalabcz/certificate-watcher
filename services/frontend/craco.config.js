module.exports = {
    webpack: {
      configure: (webpackConfig) => {
        // Find and modify the source-map-loader
        const sourceMapRule = webpackConfig.module.rules.find(rule => rule.enforce === 'pre' && rule.use && rule.use.some(use => use.loader && use.loader.includes('source-map-loader')));
        if (sourceMapRule) {
          // Exclude CSS files from source map loader
          sourceMapRule.exclude = [/\.css$/];
        }
  
        return webpackConfig;
      }
    }
  };