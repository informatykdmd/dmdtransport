/************* Main Js File ************************
    Template Name: Felona
    Author: Themescare
    Version: 1.0
    Copyright 2019
*************************************************************/

// $(window).on('load', function () {

// 	/*------------------
// 	Isotope Filter
// 	--------------------*/
// 	var $container = $('.isotope_items');
// 	$container.isotope();

// 	$('.portfolio-filter li').on("click", function () {
// 		$(".portfolio-filter li").removeClass("active");
// 		$(this).addClass("active");
// 		var selector = $(this).attr('data-filter');
// 		$(".isotope_items").isotope({
// 			filter: selector,
// 			animationOptions: {
// 				duration: 750,
// 				easing: 'linear',
// 				queue: false,
// 			}
// 		});
// 		return false;
// 	});

// });

// $(document).ready(function(){
//     var selectedFilter = "{{ selected_filter }}";

//     // Ustawienie początkowego filtra bez inicjalizacji Isotope
//     if (selectedFilter) {
//         $('.portfolio-filter li').removeClass('active');
//         $('.portfolio-filter li[data-filter="' + selectedFilter + '"]').addClass('active');

//         // Przefiltruj elementy już po załadowaniu strony
//         $(window).on('load', function () {
//             var $grid = $('.isotope_items').isotope({
//                 itemSelector: '.col-lg-4',
//                 layoutMode: 'fitRows',
//                 filter: selectedFilter // Ustawienie filtra po załadowaniu Isotope
//             });
//         });
//     } else {
//         // Inicjalizacja Isotope bez wstępnego filtrowania, gdy selectedFilter nie jest ustawiony
//         $(window).on('load', function () {
//             $('.isotope_items').isotope({
//                 itemSelector: '.col-lg-4',
//                 layoutMode: 'fitRows'
//             });
//         });
//     }
// });




