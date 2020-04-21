(function ($) {

	function check_if_compulsory_filter_checked() {
		var year = false;
		var chapter = false;
		var paper = false;
		$(".generate-filter-year").children("input").each(function () {
			if ($(this).is(":checked")) {
				year = true
			}
		});
		$(".generate-filter-chapter").children("input").each(function () {
			if ($(this).is(":checked")) {
				chapter = true
			}
		});
		$(".generate-filter-paper").children("input").each(function () {
			if ($(this).is(":checked")) {
				paper = true
			}
		});
		if (year && chapter && paper) {
			$(".generate-optional-filter").children("h2").css("color", "#000");
			$(".generate-optional-filter").children("label").css("cursor", "pointer");
			$(".generate-optional-filter").children("input").removeAttr("disabled");
		} else {
			$(".generate-optional-filter").children("h2").css("color", "#888");
			$(".generate-optional-filter").children("label").css("cursor", "not-allowed");
			$(".generate-optional-filter").children("input").prop("disabled", true);
			$(".generate-optional-filter").children("input").prop("checked", false);
		}
	}


	$(".generate-filter-year").children("input").on("click", function () {
		check_if_compulsory_filter_checked()
	});
	$(".generate-filter-paper").children("input").on("click", function () {
		check_if_compulsory_filter_checked()
	});
	$(".generate-filter-chapter").children("input").on("click", function () {
		check_if_compulsory_filter_checked()
	});

	function bind_expand_sub_question(text) {
		text.off();
		text.on("click", function () {
			$(this).siblings(".generate-question-sub-question-space").css("display", "block");
			$(this).html("Collapse Sub Questions");
			bind_collapse_sub_question($(this));
		});
	}

	function bind_collapse_sub_question(text) {
		text.off();
		text.on("click", function () {
			$(this).siblings(".generate-question-sub-question-space").css("display", "none");
			$(this).html("Expand Sub Questions");
			bind_expand_sub_question($(this));
		});
	}

	bind_expand_sub_question($(".generate-question-extend-sub-question"));

	function return_thumbnail(id) {
		return `
			<div class="generate-question-thumbnail"><span>${id}</span><img src="/static/images/icons/times-solid.svg"></img></div>
		`
	}

	function bind_add_id_to_preview() { //Use this function once any change occurs to the questions
		$(".generate-area").find("input").on("click", function () {
			var id = $(this).attr("id")
			if ($(this).is(":checked")) {
				if ($(".generate-preview:contains('" + id + "')").length > 0) {} else {
					$(".generate-preview-id").append(return_thumbnail(id))
					bind_delete_id_in_preview()
				}
			} else {
				$(".generate-question-thumbnail:contains(" + id + ")").remove();
			}
		})
	}

	bind_add_id_to_preview();

	function bind_delete_id_in_preview() { //Use this function once any addition occurs to the id preview section
		$(".generate-preview").find("img").on("click", function () {
			$(this).parent().remove();
		});
	}

	bind_delete_id_in_preview()

	$(".generate-filter").css("height", $(window).height() - 70);
	$(".generate-area").css("height", $(window).height() - 70);
	$(".generate-preview").css("height", $(window).height() - 70);

	$(window).resize(function () {
		$(".generate-filter").css("height", $(window).height() - 70);
		$(".generate-area").css("height", $(window).height() - 70);
		$(".generate-preview").css("height", $(window).height() - 70);
	});

})(jQuery);