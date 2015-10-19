import React from 'react';
import ReactDOM from 'react-dom';

export default class AppComponent extends React.Component {
	render() {
		return <p>Hello World</p>
	}
}

ReactDOM.render(<AppComponent />, document.getElementById('react-content-entrypoint'));
