const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    // Serve index.html for unknown routes so Vue Router can render 404 page
    historyApiFallback: true
  }
})
