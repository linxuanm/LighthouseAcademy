(function($) {
	$(document).scroll(function() {
		if ($(document).scrollTop() > 700) $('#nav-bar').slideDown();
		else $('#nav-bar').slideUp();
	});


	$('#reg-btn').click(function() {
		var params = {
			'email': $('#email').val(),
			'username': $('#username').val(),
			'password': $('#password').val()
		};

		responsive_post('/register', params);
	});


	$('.subject-btn').hover(function() {
		$(this).find('img').css('filter', 'invert(100%) hue-rotate(0) saturate(100) brightness(1)');
	}, function() {
		$(this).find('img').css('filter', 'invert(65%) sepia(19%) saturate(4190%) hue-rotate(186deg) brightness(102%) contrast(99%)');
	});
})(jQuery);