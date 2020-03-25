(function($) {
	function bind_expand_sub_question(text){
		text.off();
		text.on("click",function(){
			$(this).siblings(".search-question-sub-question-space").css("display","block");
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

	$(".search-filter").css("height",$(window).height() - 70);
	$(".search-area").css("height",$(window).height() - 70);

	$(window).resize(function(){
		$(".search-filter").css("height",$(window).height() - 70);
		$(".search-area").css("height",$(window).height() - 70);
	});

	$("#submit-search").on("click", function(){
		window.location.replace("/search/" + $(this).siblings("input").val());
	});

	$("#input-search").on("keyup", function(e){
		if (e.keyCode === 13) {
			window.location.replace("/search/" + $(this).val());
		}
	})


	bind_expand_sub_question($(".search-question-extend-sub-question"));
})(jQuery);