/************* Main Js File ************************
    Template Name: Sukorna
    Author: Iramflex
    Version: 1.0
    Copyright 2022
*************************************************************/


/*------------------------------------------------------------------------------------
    
JS INDEX
=============
01 - Data Background
02 - Hero Slider
03 - Project Slider
04 - Team Slider
05 - Testimonial Slider
06 - Project Details Slider
07 - Jarallax Background
08 - Header Search
09 - Video Popup
10 - Progress Bar
11 - Pricing Filter
12 - Wow Animation
13 - Responsive Menu
14 - Back To Top

-------------------------------------------------------------------------------------*/


(function ($) {
	"use strict";

	jQuery(document).ready(function ($) {
		/* 
		=================================================================
		01 - Data Background
		=================================================================	
		*/
		$("[data-background").each(function () {
			$(this).css("background-image", "url( " + $(this).attr("data-background") + "  )");
		});

		/* 
		=================================================================
		02 - Hero Slider
		=================================================================	
		*/

		$(".hero-slider").owlCarousel({
			animateOut: 'fadeOutLeft',
			animateIn: 'fadeIn',
			items: 2,
			nav: false,
			dots: true,
			autoplayTimeout: 7000,
			autoplaySpeed: 2000,
			autoplay: true,
			loop: true,
			navText: ["<i class='fa fa-long-arrow-left'><i>", "<i class='fa fa-long-arrow-right'><i>"],
			mouseDrag: true,
			touchDrag: true,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 1
				},
				600: {
					items: 1
				},
				750: {
					items: 1
				},
				1000: {
					items: 1
				},
				1200: {
					items: 1
				}
			}
		});


		$(".hero-slider").on("translate.owl.carousel", function () {
			$(".hero-slider .hero-title").removeClass("animated fadeInDown").css("opacity", "0");
			$(".hero-slider .banner-txt p").removeClass("animated fadeInUp").css("opacity", "0");
			$(".hero-slider .btn_group").removeClass("animated fadeInDown").css("opacity", "0");
		});
		$(".hero-slider").on("translated.owl.carousel", function () {
			$(".hero-slider .hero-title").addClass("animated fadeInDown").css("opacity", "1");
			$(".hero-slider .banner-txt p").addClass("animated fadeInUp").css("opacity", "1");
			$(".hero-slider .btn_group").addClass("animated fadeInDown").css("opacity", "1");
		});

		/* 
		=================================================================
		03 - Project Slider
		=================================================================	
		*/

		$(".recent-project-slider").owlCarousel({
			items: 4,
			nav: false,
			dots: true,
			autoplayTimeout: 7000,
			autoplaySpeed: 2000,
			autoplay: true,
			loop: true,
			navText: ["<i class='fa fa-long-arrow-left'><i>", "<i class='fa fa-long-arrow-right'><i>"],
			mouseDrag: true,
			touchDrag: true,
			margin: 30,
			center: true,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 1
				},
				600: {
					items: 2
				},
				750: {
					items: 3
				},
				1000: {
					items: 3
				},
				1200: {
					items: 4
				}
			}
		});

		/* 
		=================================================================
		04 - Team Slider
		=================================================================	
		*/

		$(".team-slider").owlCarousel({
			items: 3,
			nav: false,
			dots: true,
			autoplayTimeout: 8000,
			autoplay: true,
			loop: true,
			navText: ["<span class='fas fa-angle-left'></span>", "<span class='fas fa-angle-right'></span>"],
			mouseDrag: true,
			touchDrag: true,
			margin: 30,
			center: true,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 1
				},
				600: {
					items: 2,
					center: false
				},
				750: {
					items: 2,
					center: true
				},
				1000: {
					items: 3
				},
				1200: {
					items: 3
				}
			}
		});

		/* 
		=================================================================
		05 - Testimonial Slider
		=================================================================	
		*/

		$(".testimonial-slider").owlCarousel({
			items: 1,
			nav: true,
			dots: false,
			autoplayTimeout: 8000,
			autoplay: true,
			loop: true,
			navText: ["<span class='fas fa-angle-left'></span>", "<span class='fas fa-angle-right'></span>"],
			mouseDrag: true,
			touchDrag: true,
			margin: 30,
			center: true
		});

		/* 
		=================================================================
		06 - Project Details Slider
		=================================================================	
		*/

		$(".project-details-slider").owlCarousel({
			items: 1,
			nav: true,
			dots: false,
			autoplayTimeout: 8000,
			autoplay: true,
			loop: true,
			navText: ["<span class='fas fa-angle-left'></span>", "<span class='fas fa-angle-right'></span>"],
			mouseDrag: true,
			touchDrag: true,
			margin: 30,
			center: true
		});

		/* 
		=================================================================
		07 - Jarallax Background
		=================================================================	
		*/
		$('.jarallax').jarallax({
			speed: 0.5
		});

		/* 
		=================================================================
		08 - Header Search
		=================================================================	
		*/
		$('#close-btn').click(function () {
			$('#search-overlay').fadeOut();
			$('#search-btn').show();
		});
		$('.search-toggle').click(function () {
			$('#search-overlay').fadeIn();
		});


		/* 
		=================================================================
		09 - Video Popup
		=================================================================	
		*/

		$('.popup-box').magnificPopup({
			disableOn: 700,
			type: 'iframe',
			mainClass: 'mfp-fade',
			removalDelay: 160,
			preloader: false,
			fixedContentPos: false
		});


		/*==============================
		10 - Progress Bar
		==============================*/
		$(window).on("scroll", function () {

			var bodyScroll = $(window).scrollTop()

			if (bodyScroll > 1400) {

				$('#bar2').barfiller({
					duration: 2000
				});

				$('#bar3').barfiller({
					duration: 1600
				});

				$('#bar4').barfiller({
					duration: 1200
				});

				$('#bar5').barfiller({
					duration: 800
				});

				$('#bar6').barfiller({
					duration: 800
				});
			}
		});


		/*=================================================================
		11 - Pricing Filter
		=================================================================	
		*/
		$('#checkbox[type="checkbox"]').on("click", function () {

			if ($(this).prop("checked") == true) {
				$('.priceHide').show(0);
				$('.priceShow').hide(0);
			} else if ($(this).prop("checked") == false) {
				$('.priceHide').hide(0);
				$('.priceShow').show(0);
			}
		});

		/*==============================
		12 - Wow Animation
		==============================*/
		new WOW().init();

		/*==============================
		13 - Responsive Menu
		==============================*/
		$(".mainmenu ul li:has(ul)").addClass("has-submenu");
		$(".mainmenu ul li:has(ul.small-dropdown)").addClass("small-submenu");
		$(".mainmenu ul li ul").addClass("sub-menu");
		$(".mainmenu ul.dropdown li").hover(function () {
			$(this).addClass("hover")
		}, function () {
			$(this).removeClass("hover")
		});

		var $menu = $("#menu"),
			$menulink = $("#spinner-form"),
			$menuTriggercont = $(".spinner-master"),
			$menuTrigger = $(".has-submenu > a");
		$menulink.click(function (e) {
			$menulink.toggleClass("active");
			$menu.toggleClass("active");
			$menuTriggercont.toggleClass("active");
		});

		$menuTrigger.click(function (e) {
			e.preventDefault();
			var t = $(this);
			t.toggleClass("active").next("ul").toggleClass("active")
		});

		$(".mainmenu ul li:has(ul)");
        
        /* 
		=================================================================
		14 - Back To Top
		=================================================================	
		*/
		if ($("body").length) {
			var btnUp = $('<div/>', {
				'class': 'btntoTop'
			});
			btnUp.appendTo('body');
			$(document).on('click', '.btntoTop', function () {
				$('html, body').animate({
					scrollTop: 0
				}, 700);
			});
			$(window).on('scroll', function () {
				if ($(this).scrollTop() > 200) $('.btntoTop').addClass('active');
				else $('.btntoTop').removeClass('active');
			});
		}



	});


}(jQuery));