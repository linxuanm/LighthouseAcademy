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



	bind_expand_sub_question($(".search-question-extend-sub-question"));
})(jQuery);