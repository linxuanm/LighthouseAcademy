function responsive_post(url, params) {
	$.post(
		url,
		params,
		function(data) {
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
				case 5: //Questions successfully added to database. Proceed to process image
					if (image_array.length != 0) {
						$("#submit-button").html("Uploading Image")
						image_array.forEach(function(item, index){
							formdata = new FormData()
							id = item[1]
							id_code = $("#" + id + "").parents(".add-qs-question-space").find(".add-qs-question-id-input").val()
							formdata.append("file",item[0])
							formdata.append("id_code",id_code.replace("-0-", "-" + item[2] + "-"))
							formdata.append("for_sub_question",item[2])
							if (index == image_array.length - 1) {
								$.ajax({
									type: 'POST',
									url:  '/upload_image',
									data: formdata,
									contentType: false,
									cache: false,
									processData: false,
									success: function(data) {
										$("#submit-button").html("Uploaded " + image_array.length + " image")
									},
								});
							}else{
								$.ajax({
									type: 'POST',
									url:  '/upload_image',
									data: formdata,
									contentType: false,
									cache: false,
									processData: false,
									success: function(data) {
									},
								});
							}
						})
					}else{
						$("#submit-button").html("Upload Success")
					}
					break;
			}
		},
	);
}