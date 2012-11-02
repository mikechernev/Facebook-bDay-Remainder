setMenuWidth = function() {
	var width = 0;
	$("#menu li").each(function () {
		width += $(this).width();
	});
	$("#menu").width(width);
};

initInfo = function() {
	var width = mikeWidth*2 + atWidth*2 + wwwWidth*2 + $("#mikechernev").width();
	$("#content").width(width);
};

resetPadding = function() {
	$("#content span").css({"color": "", "padding-left": ""});
};

$(function() {

	mikeWidth = $("#mike").width();
	atWidth = $("#at").width();
	wwwWidth = $("#www").width();

	setMenuWidth();
	initInfo();

	$("#menu").mouseleave(function() {
		resetPadding();
		var padding = mikeWidth + atWidth + wwwWidth;
		$("#mike, #at, #www, #dotcom").hide();
		$("#mikechernev").css("padding-left", padding);
	});
	$("#menu").mouseleave();

	$("#siteLink").hover(function(e) {
		resetPadding();
		var padding = mikeWidth + atWidth;
		$("#www, #dotcom").show();
		$("#mike, #at").hide();
		$("#www").css("padding-left", padding);
		$("#siteInfo").slideDown();
	}, function(e) {
		$("#siteInfo").slideUp();
	});

	$("#emailLink").hover(function(e) {
		resetPadding();
		var padding =  wwwWidth;
		$("#www").hide();
		$("#mike, #at, #dotcom").show();
		$("#content span").css("color", "#C0361A");
		$("#mike").css("padding-left", padding);
		$("#emailInfo").slideDown();
	}, function(e) {
		$("#emailInfo").slideUp();
	});
	
	$("#skypeLink").hover(function(e) {
		resetPadding();
		var padding = mikeWidth + atWidth + wwwWidth;
		$("#content span").css("color", "#00AFF0");
		$("#mike, #www, #at, #dotcom").hide();
		$("#mikechernev").css("padding-left", padding);
		$("#skypeInfo").slideDown();
	}, function(e) {
		$("#skypeInfo").slideUp();
	});

	$("#twitterLink").hover(function(e) {
		resetPadding();
		var padding = mikeWidth + wwwWidth;
		$("#content span").css("color", "#019AD2");
		$("#at").show();
		$("#mike, #www, #dotcom").hide();
		$("#at").css("padding-left", padding);
		$("#twitterInfo").slideDown();
	}, function(e) {
		$("#twitterInfo").slideUp();
	});

	$("#failbookLink").hover(function(e) {
		resetPadding();
		var padding = mikeWidth + atWidth + wwwWidth;
		$("#content span").css("color", "#3B5998");
		$("#mike, #www, #at, #dotcom").hide();
		$("#mikechernev").css("padding-left", padding);
		$("#failbookInfo").slideDown();
	}, function(e) {
		$("#failbookInfo").slideUp();
	});

	$("#aboutLink").hover(function(e) {
		$("#menu").mouseleave();
		$("#aboutInfo").slideDown();
	}, function() {
		$("#aboutInfo").slideUp();
	}).click(function(e) {
		e.preventDefault();
		alert("There's nothing interesting about me :)");
	});
	
	$("#users").hover(function(e) {
		$("#users_count_info").fadeIn();
	}, function() {
		$("#users_count_info").fadeOut();
	});
});