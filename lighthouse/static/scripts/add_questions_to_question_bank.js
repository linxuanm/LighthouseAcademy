(function($) {

	const new_answer = `
	<div class="ms-answer-space">
		<label class="ms-answer-label">&nbsp</label>
		<textarea type="text" class="ms-answer-input" placeholder="Enter Answer Here (Latex Support)"></textarea>
		<p>Answer preview with latex conversion</p>
		<p class="latex-conversion" id="latex-conversion-q-2"></p>
	</div>
	`;

	const new_credit = `
	<div class="ms-credit-space">
		<label class="ms-credit-label">&nbsp</label>
		<textarea type="text" class="ms-credit-input" placeholder="M1"></textarea>
		<div class="ms-delete-credit"><p>Delete Mark</p></div>
	</div>
	`;

	const new_sub_question = `
	<div class="sub-question-space">
		<div class="topbar">
			<img class="trash" src="/static/images/icons/times-solid.svg"></img>
			<input class="question-id-input" placeholder="Type question id or select =>" style="float:right"></input>
		</div>
		<label class="question-label">Sub-Question</label>
		<textarea type="text" class="question-input" placeholder="Enter Question Here (Latex Support)"></textarea>
		<p>Question preview with latex conversion</p>
		<p class="latex-conversion"></p>
	</div>`;

	var image_array = [];
	var image_id = 0;

	var sub_question_ms_space = 
		`
		<div class="ms-sub-question-space">
			<div class="ms-answer-block">
				<div class="ms-answer-space">
					<label class="ms-answer-label">Sub-Question Answer</label>
					<textarea type="text" class="ms-answer-input" placeholder="Enter Answer Here (Latex Support)"></textarea>
					<p>Answer preview with latex conversion</p>
					<p class="latex-conversion" id="latex-conversion-q-2"></p>
				</div>
			</div>
			<div class="ms-credit-block">
				<div class="ms-credit-space">
					<label class="ms-credit-label">Marks</label>
					<textarea type="text" class="ms-credit-input" placeholder="M1"></textarea>
					<div class="ms-add-credit"><p>Add Marks</p></div>
				</div>
			</div>
		</div>
		
		`;

	function nl2br (str, is_xhtml) {
		var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';
		return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2');
	}

	function bind_latex_conversion(textarea){
		textarea.on("input",function(){
			$(this).parent().children(".latex-conversion").last().html(nl2br($(this).val()));
			MathJax.typesetClear();
			MathJax.typeset($(this).parent().find(".latex-conversion"));
			$(this).autoheight();
			$(this).css("width","calc(100.3%)");
		});
	}

	// Delete main question or sub question
	function bind_trash(trashicon){
		trashicon.on("click",function(){
			if (confirm("Delete this sub-question?")) {
				var question_space = $(this).parents(".question-space");
				var sub_q_index = question_space.find(".sub-question-space").index($(this).parents(".sub-question-space"));
				$(".ms-sub-question-space:eq(" + sub_q_index + ")").remove();
				$(this).parents(".sub-question-space").remove();
			}
		});
	}

	// Sync answer space height with credit(mark) space height
	function bind_sync_answer_and_mark_div_height(){
		$(".ms-answer-input").each(function(){
			var current_answer_space = $(this).parents(".ms-answer-space");
			var current_index = $(this).parents(".ms-answer-block").find(".ms-answer-space").index(current_answer_space);
			var current_credit_space = $(this).parents(".ms-answer-block").siblings(".ms-credit-block").find(".ms-credit-space:eq(" + current_index + ")");
			current_credit_space.css("height", current_answer_space.css("height"));
		});
		$(".ms-answer-input").on("input", function(){
			var current_answer_space = $(this).parents(".ms-answer-space");
			var current_index = $(this).parents(".ms-answer-block").find(".ms-answer-space").index(current_answer_space);
			var current_credit_space = $(this).parents(".ms-answer-block").siblings(".ms-credit-block").find(".ms-credit-space:eq(" + current_index + ")");
			current_credit_space.css("height", current_answer_space.css("height"));
		});
	
	}

	// Add mark input for sub-question on new sub-question
	function sync_add_sub_question(question_space){
		question_space.append(sub_question_ms_space);
		var added_div = question_space.children(".ms-sub-question-space").last();
		bind_add_credit(added_div.find(".ms-add-credit"));
		bind_latex_conversion(added_div.find(".ms-answer-space").find(".ms-answer-input"));
		bind_upload_image(added_div.find(".ms-answer-space"));
		bind_sync_answer_and_mark_div_height();
	}

	// event for "add mark button"
	function bind_add_credit(add_mark_button){
		add_mark_button.on("click",function(){
			var great_grandparent = $(this).parent().parent().parent();
			great_grandparent.find(".ms-credit-block").first().append(new_credit);
			great_grandparent.find(".ms-answer-block").first().append(new_answer);
			var target_answer_block = $(this).parent().parent().parent().children(".ms-answer-block").children(".ms-answer-space").last();
			var target_credit_block = $(this).parent().parent().find(".ms-delete-credit").last().parent();
			bind_upload_image(target_answer_block);
			bind_latex_conversion(great_grandparent.find(".ms-answer-block").find(".ms-answer-input").last());
			$(this).parent().parent().find(".ms-delete-credit").last().on("click",function(){
				target_answer_block.remove();
				target_credit_block.remove();
			});
			bind_sync_answer_and_mark_div_height();
		});
	}

	function validate_user_input(){

		var empty_fields = [];
		var id_codes = [];
		var repeated_id_code = [];
		var bad_id_code_regex = [];
		var bad_credit_regex = [];
		

		$(".question-input").each(function(){
			if (!$(this).val()) {
				empty_fields.push($(this));
			}
		});
		$(".ms-answer-input").each(function(){
			if (!$(this).val()) {
				empty_fields.push($(this));
			}
		});
		$(".ms-credit-input").each(function(){
			if (!$(this).val()) {
				empty_fields.push($(this));
			}
			if (!$(this).val().match(CREDIT_REGEX)) {
				bad_credit_regex.push($(this));
			}
		});
		$(".question-id-input").each(function(){
			if (!$(this).val()) {
				empty_fields.push($(this));
			}
			//Check if id code input is for sub question and check against corresponding regex
			if ($(this).parent().parent().hasClass("sub-question-space")) {
				if (!$(this).val().match(ID_CODE_REGEX_FOR_SUB_QUESTION)) {
					bad_id_code_regex.push($(this));
				}
			}else{
				if (!$(this).val().match(ID_CODE_REGEX_FOR_QUESTION)) {
					bad_id_code_regex.push($(this));
				}
			}
			
			if (id_codes.includes($(this).val())) {
				repeated_id_code.push($(this));
			}
			id_codes.push($(this).val());
		});

		if (empty_fields.length != 0) {
			empty_fields.forEach(function(item){
				item.addClass("invalid-input");
			});
			alert("Fields Cannot Be Empty");
			return false;
		}else{
			if (repeated_id_code.length != 0) {
				repeated_id_code.forEach(function(item){
					item.addClass("invalid-input");
				});
				alert("Question ID Must Be Unique");
				return false;
			}else{
				if (bad_id_code_regex.length != 0) {
					bad_id_code_regex.forEach(function(item){
						item.addClass("invalid-input");
					});
					alert("Invalid Question ID Format");
					return false;
				}else{
					if (bad_credit_regex.length != 0) {
						bad_credit_regex.forEach(function(item){
							item.addClass("invalid-input");
						});
						alert("Invalid Marks Format");
						return false;
					}else{
						return true;
					}
				}
			}
		}
	}

	function submit_data_to_server(){
		var formData = new FormData();
		var orders = [];
		var id_codes = [];
		image_array.forEach(function(item) {
			if (item.div.hasClass("ms-answer-space")) {
				item.order = item.div.parent().find(".ms-answer-space").index(item.div);
				if (item.div.parents(".ms-sub-question-space").length) {
					var ms_index = $(".ms-sub-question-space").index(item.div.parents(".ms-sub-question-space"));
					item.id_code = $(".sub-question-space:eq("+ ms_index +")").find(".question-id-input").val();
				}else{
					item.id_code = $(".question-space").find(".question-id-input").val()
				}
			} else {
				item.id_code = item.div.find(".question-id-input").val();
				item.order = "none";
			}
			formData.append("files", item.file);
			orders.push(item.order);
			id_codes.push(item.id_code);
		});
		formData.append("id_codes", id_codes);
		formData.append("orders", orders);

		var params = {"question":{}};
		
		$(".question-space").each(function(){
			var id_code = $(this).find(".question-id-input").val();
			var has_image = false;
			image_array.forEach(function(item) {
				if (item.id_code == id_code && item.order == "none") {
					has_image = true;
				}
			});

			params.question.text = $(this).children(".question-input").val();
			params.question.id_code = id_code;
			params.question.has_image = has_image;

			params.question.marks = {};
			var answer_text = [];
			$(this).children(".ms-answer-block").find(".ms-answer-input").each(function() {
				answer_text.push($(this).val())
			})
			var answer_credit = [];
			$(this).children(".ms-credit-block").find(".ms-credit-input").each(function() {
				answer_credit.push($(this).val())
			})
			for (var i = 0; i < answer_text.length; i++) {
				var answer_has_image = false;
				image_array.forEach(function(item) {
					if (item.id_code == id_code && item.order == i) {
						answer_has_image = true;
					}
				})
				params.question.marks[i] = {'text': answer_text[i], 'credit': answer_credit[i], 'has_image': answer_has_image};
			}
			
			
			params.question.sub_questions = {};
			$(this).find(".sub-question-space").each(function () {
				var sub_id_code = $(this).find(".question-id-input").val();
				var order = $(".question-space").find(".sub-question-space").index($(this));
				var has_image = false;
				image_array.forEach(function(item) {
					if (item.id_code == sub_id_code && item.order == "none") {
						has_image = true;
					}
				});
				params.question.sub_questions[sub_id_code] = {
					"id_code": sub_id_code,
					"text": $(this).children(".question-input").val(),
					"has_image": has_image,
				};
				params.question.sub_questions[sub_id_code].marks = {};
				var answers = $(".question-space").find(".ms-sub-question-space:eq(" + order + ")");
				var answer_text = [];
				answers.find(".ms-answer-input").each(function() {
					answer_text.push($(this).val())
				})
				var answer_credit = [];
				answers.find(".ms-credit-input").each(function() {
					answer_credit.push($(this).val())
				})
				for (var i = 0; i < answer_text.length; i++) {
					answer_has_image = false;
					image_array.forEach(function(item) {
						if (item.id_code == sub_id_code && item.order == i) {
							answer_has_image = true;
						}
					})
					params.question.sub_questions[sub_id_code].marks[i] = {'text': answer_text[i], 'credit': answer_credit[i], 'has_image': answer_has_image};
				}
			})
		});
		$.ajax({
			type: 'POST',
			url: '/upload_image',
			data: formData,
			contentType: false,
			cache: false,
			processData: false,
			success: function(data){
				if (data.image_upload == "success") {
					$.ajax({
						type: 'POST',
						url: '/add_qs',
						data: {'data': JSON.stringify(params)},
						success: function(data) {
							handle_server_response(data);
							if (data.code == 5) {
								$("#submit-button").html("Upload Success");
							}
						}
					}
				);
				}
			},
			error: function(){
				$("#submit-button").html("Error! Please Contact the Lighthouse Team");
			}
		});
		
	}

	function bind_upload_image(div){

		div.on("drag dragstart dragend dragover dragenter dragleave drop",function(e){
			e.preventDefault();
			e.stopPropagation();
		})
		.on("dragenter dragover",function(){
			$(this).addClass("drag-on");
		})
		.on("dragleave dragend drop",function(){
			$(this).removeClass("drag-on");
		})
		.on("drop",function(e){
			var question_id;
			if (div.hasClass("ms-answer-space")) {
				question_id = div.find(".ms-answer-input").first().attr("id");
			}else{
				question_id = div.find(".question-input").first().attr("id");
			}
			var droppedFiles = e.originalEvent.dataTransfer.files;
			var reader = new FileReader();
			if (droppedFiles.length != 1){
				alert("Please upload only one image");
			}else{
				var target_file = droppedFiles[0];
				reader.readAsDataURL(target_file);
				if (target_file.type.indexOf("jpg") == -1 && target_file.type.indexOf("jpeg") == -1 && target_file.type.indexOf("png") == -1) {
					alert("Lighthouse only supports images of format jpg and png");
				}else{
					if ($.inArray(question_id, $.map(image_array, function(v) { return v[1]; })) > -1) {
						alert("Currently, one question should only have one image");
					}else{
						reader.onload = function(){
							var label_name;
							if (div.hasClass("ms-answer-space")) {
								label_name = "ms-answer-label";
							}else{
								label_name = "question-label";
							}
							div.find("." + label_name).first().after($("<img>",{ //Cross Icon
								src:"/static/images/icons/times-solid.svg",
								class:"image-icons",
								style:"margin-left:0px",
								id: image_id
							}).on("click",function(){
								$(this).siblings(".image-icons").remove();
								var id =  $(this).attr('id');
								$(this).remove();
								image_array.forEach(function(item, index) {
									if (item.id == id){
										image_array.splice(index, 1);
									}
								});
							})).after($("<img>",{ //Image icon
								src:"/static/images/icons/file-image-solid.svg",
								class:"image-icons",
							}));
							image_array.push({'file': target_file, 'div': div, 'id': image_id});
							image_id ++
						};
					}
				}
			}
		});
	}
	var question_space = $(".question-space");
	bind_upload_image(question_space);
	bind_upload_image(question_space.find(".ms-answer-space"));
	bind_latex_conversion(question_space.find(".question-input"));
	bind_latex_conversion(question_space.find(".ms-answer-space").find(".ms-answer-input"));
	bind_add_credit(question_space.find(".ms-add-credit"),1);
	bind_sync_answer_and_mark_div_height();
	question_space.find(".add-sub-q").on("click",function(){
		$(this).before(new_sub_question);
		var added_div = $(this).parent().children(".sub-question-space").last();
		bind_upload_image(added_div);
		bind_latex_conversion(added_div.children("textarea"));
		sync_add_sub_question($(this).parent());
		bind_trash(added_div.find(".trash"));
		bind_sync_answer_and_mark_div_height();
	});

	$(".submit-button").on("click", function(){
		if (validate_user_input()) {
			submit_data_to_server();
		}
	});


})(jQuery);