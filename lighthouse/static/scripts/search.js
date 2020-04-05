(function($) {

	//Showing and hiding sub quesitons
	function bind_expand_sub_question(text){
		text.off();
		text.on("click",function(){
			$(this).siblings(".search-question-sub-question-space").css("display","inline-block");
			$(this).html("Collapse Sub Questions");
			bind_collapse_sub_question($(this));
		});
	}

	function bind_collapse_sub_question(text){
		text.off();
		text.on("click",function(){
			$(this).siblings(".search-question-sub-question-space").css("display","none");
			$(this).html("Expand Sub Questions");
			bind_expand_sub_question($(this));
		});
	}

	bind_expand_sub_question($(".search-question-extend-sub-question"));

	//Some insignificant line escaping
	if ($(window).width() <= 600){
		$(".search-question-details").find("span:eq(0)").prepend("</br>")
		$(".search-question-details").find("span:eq(1)").prepend("</br>")
	}
			
	//Get user search and send it to server
	$("#submit-search").on("click", function(){
		if ($("#input-search").val() !== "") {
			window.location.replace("/search?search=" + $("#input-search").val())
		}else{
			window.location.replace("/search")
		}

	});

	$("#input-search").on("keyup", function(e){
		if (e.keyCode === 13) {
			if ($("#input-search").val() !== "") {
				window.location.replace("/search?search=" + $("#input-search").val())
			}else{
				window.location.replace("/search")
			}
		}
	})

	//Not original function that returns query string as some kind of dict
	function getUrlVars(){
		var vars = [], hash
		var hashes = window.location.href.slice(window.location.href.indexOf("?") + 1).split("&")
		for (var i = 0; i < hashes.length; i++) {
			hash = hashes[i].split("=")
			vars.push(hash[0])
			vars[hash[0]] = hash[1]
		}
		return vars
	}

	//retain checked filter when page is refreshed caused by filter update
	function retain_checked_filter(filter_target){
		if (typeof getUrlVars()[filter_target] !== "undefined") {
			$(".filter-" + filter_target).find($("input")).each(function(){
				if (filter_target == "paper") {
					var id = $(this).attr("id").substr($(this).attr("id").length - 1)
				}else if (filter_target == "chapter"){
					pattern = /(?:-(\w+)){1}/
					var id = $(this).attr("id").match(pattern)[1]
				}else{
					var id = $(this).attr("id")
				}
				if (getUrlVars()[filter_target].split(",").indexOf(id) !== -1) {
					$(this).prop("checked", true)
				}
			})
		}
	}

	retain_checked_filter("season")
	retain_checked_filter("paper")
	retain_checked_filter("chapter")
	retain_checked_filter("difficulty")

	function format_filter_url(filter_array, filter_target, target){
		if (filter_array.length != 0) {
			target = target + filter_target + "=" + filter_array.toString() + "&"
			return target
		}else{
			return target
		}
	}

	//Collect user filter options and send it to the server
	function collect_and_post_filter(){
		//Get current path with query string
		console.log(getUrlVars())
		if (window.location.search !== "") {
			if (typeof getUrlVars()["search"] !== "undefined") {
				var target_url = window.location.pathname + "?search=" + getUrlVars()["search"] + "&"
			}else{
				var target_url = window.location.pathname + "?"
			}
		}else{
			var target_url = window.location.pathname + window.location.search + "?"
		}

		array_season = []
		$(".filter-season").children("input").each(function(){
			if ($(this).is(":checked")) {
				array_season.push($(this).attr("id"))
			}
		})
		target_url = format_filter_url(array_season, "season", target_url)

		array_paper = []
		$(".filter-paper").children("input").each(function(){
			if ($(this).is(":checked")) {
				array_paper.push($(this).attr("id").substr($(this).attr("id").length - 1))
			}
		})
		target_url = format_filter_url(array_paper, "paper", target_url)

		pattern = /(?:-(\w+)){1}/
		array_chapter = []
		$(".filter-chapter").children("input").each(function(){
			if ($(this).is(":checked")) {
				array_chapter.push($(this).attr("id").match(pattern)[1])
			}
		})
		target_url = format_filter_url(array_chapter, "chapter", target_url)

		array_difficulty = []
		$(".filter-difficulty").children("input").each(function(){
			if ($(this).is(":checked")) {
				array_difficulty.push($(this).attr("id"))
			}
		})
		target_url = format_filter_url(array_difficulty, "difficulty", target_url)

		if ($("#year-start").val() !== "") {
			target_url = target_url + "year-start" + "=" + $("#year-start").val() + "&"
		}

		if ($("#year-end").val() !== "") {
			target_url = target_url + "year-end" + "=" + $("#year-end").val() + "&"
		}

		if (target_url.slice(-1) === "&") {
			target_url = target_url.slice(0, -1)
			console.log(target_url)
		}
		window.location.replace(target_url)
	}

	$(".search-filter").find("input").on("keyup", function(e){
		if (e.keyCode === 13) {
			collect_and_post_filter()
			console.log("hi")
		}
	});
	$(".search-filter").find("input").on("click", function(){
		collect_and_post_filter()
	});
	$(".search-filter").find("button").on("click", function(){
		collect_and_post_filter()
	});


	//Initinalize Cookies if not defined
	if (typeof Cookies.get("selected_questions") === "undefined") {
		Cookies.set("selected_questions", JSON.stringify([]))
		Cookies.set("selected_sub_questions", JSON.stringify([]))
	}

	//Tick all question that already selected when reloading the page
	var selected_questions = JSON.parse(Cookies.get("selected_questions"))
	var selected_sub_questions = JSON.parse(Cookies.get("selected_sub_questions"))
	$("input").each(function(){
		if (selected_questions.indexOf($(this).attr("id")) !== -1 || selected_sub_questions.indexOf($(this).attr("id")) !== -1) {
			$(this).prop("checked", true)
		}
	})
	

	//update, show or, hide question count at the nav bar
	function update_question_count(){
		var selected_questions = JSON.parse(Cookies.get("selected_questions"))
		var selected_sub_questions = JSON.parse(Cookies.get("selected_sub_questions"))
		if (selected_questions.length == 0 && selected_sub_questions.length == 0) {
			$(".nav-counting-hint").css("display", "none")
		}else{
			$(".nav-counting-hint").css("display", "block")
			$("#question_count").html(selected_questions.length)
			$("#sub_question_count").html(selected_sub_questions.length)
		}
	}

	update_question_count()

	//Detect user ticking questions and add questions to a array selected_questions and selected sub_questions
	//Automatically check/uncheck the sub questions when checking/unchecking the main question
	$(".search-result-space").children("input").on("click",function(){
		var selected_questions = JSON.parse(Cookies.get("selected_questions"))
		var selected_sub_questions = JSON.parse(Cookies.get("selected_sub_questions"))

		if ($(this).is(":checked")) {
			selected_questions.push($(this).attr("id"))
			Cookies.set("selected_questions", JSON.stringify(selected_questions))
			var waiting_to_be_add = []			
			$(this).parent().find(".search-question-sub-question-space").children("input").each(function(){
				waiting_to_be_add.push($(this).attr("id"))
				$(this).prop("checked", true)
			})
			selected_sub_questions.push.apply(selected_sub_questions, waiting_to_be_add)
			Cookies.set("selected_sub_questions", JSON.stringify(selected_sub_questions))
			update_question_count()
		}else{
			var id = $(this).attr("id")
			selected_questions = selected_questions.filter(function(e){ return e !== id})
			Cookies.set("selected_questions", JSON.stringify(selected_questions))

			accumulated_target = []
			$(this).parent().find(".search-question-sub-question-space").children("input").each(function(){
				var id = $(this).attr("id")
				selected_sub_questions = selected_sub_questions.filter(function(e){ return e !== id })
				$(this).prop("checked", false)
			})
			Cookies.set("selected_sub_questions", JSON.stringify(selected_sub_questions))
			update_question_count()
		}
	})
	$(".search-question-sub-question-space").children("input").on("click", function(){
		var selected_sub_questions = JSON.parse(Cookies.get("selected_sub_questions"))
		if ($(this).is(":checked")) {
			selected_sub_questions.push($(this).attr("id"))
			Cookies.set("selected_sub_questions", JSON.stringify(selected_sub_questions))
			update_question_count()
		}else{
			var id = $(this).attr("id")
			selected_sub_questions = selected_sub_questions.filter(function(e){ return e !== id})
			Cookies.set("selected_sub_questions", JSON.stringify(selected_sub_questions))
			update_question_count()
		}
	})

	//Delete Question from database
	$("#delete_selected_questions").on("click", function(){
		if (confirm("You are about to delete " + selected_questions.length + " questions and " + selected_sub_questions.length + " sub-questions")) {
			formdata = new FormData()
			formdata.append("purpose", "delete")
			formdata.append("questions_to_delete", selected_questions)
			formdata.append("sub_questions_to_delete", selected_sub_questions)
			$.ajax({
				type: 'POST',
				url:  window.location.pathname,
				data: formdata,
				contentType: false,
				cache: false,
				processData: false,
				success: function(data) {
					console.log("hi")
				},
			});
		}
	})

	
})(jQuery);