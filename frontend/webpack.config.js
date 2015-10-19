var path = require('path');

module.exports = {
	devtool: 'source-map',
	entry: './src/AppComponent.jsx',
	output: {
		path: __dirname,
		filename: 'bundle.js'
	},
	module: {
		loaders: [
			{
				test: /\.jsx?$/,
				include: /src/,
				loader: 'babel'
			}
		]
	},
	resolve: {
		alias: {
		}
	}
};
