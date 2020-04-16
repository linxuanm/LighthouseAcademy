function responsive_post(url, params) {
	$.post(
		url,
		params,
		function(data) {
			handle_server_response(data)
		}
	)
}

function handle_server_response(data){
	switch (data.code) {
		case 0: // Does nothing.
			break;
		case 1: // Goes to URL.
			window.location = data.content;
			break;
		case 2: // Infos the user.
			alert(data.content);
			break;
		case 3: // Warns the user.
			alert('Warning: ' + data.content);
			break;
		case 4: // Errors the user.
			alert('Error: ' + data.content);
			break;
	}
}
