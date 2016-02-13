
!(function($) {

	'use strict';

	var ModalPopover = function(element, options) {
		this.init('modalpopover', element, options);
	};

	ModalPopover.prototype = $.extend({}, $.fn.popover.Constructor.prototype, {
		constructor: ModalPopover,
		firstShow: true,		
		show: function() {
			$.fn.popover.Constructor.prototype.show.apply(this);

			if(this.firstShow) {
				this.tip().click(function(event) {
					this.firstShow = false;
					return false;
				})
			}
		}
	});

	$.fn.modalpopover = function(option) {
		return this.each(function() {
			var $this = $(this), 
				data = $this.data('modalpopover'),
		        options = typeof option == 'object' && option;

			if (!data) {
				$this.data('modalpopover', (data = new ModalPopover(this, options)))
			} 

			if (typeof option == 'string') {
				data[option]()
			} 

		})
	};

	$.fn.modalpopover.Constructor = ModalPopover;
	$.fn.modalpopover.defaults = $.extend({}, $.fn.popover.defaults);

    var prevClickedElem = null;

	$(document).click(function(event) {
		var $target = $(event.target),
			$this = $(this),
			curentPopover = $this.data('modalpopover');

        if($target.data('modalpopover') && (!$this.data('modalpopover') || $target != prevClickedElem)) {
			if(curentPopover) curentPopover.hide();
			$target.modalpopover('show');
			$this.data('modalpopover', $target.data('modalpopover'));
            prevClickedElem = $target;
		} else {
			if(curentPopover) curentPopover.hide();
			$this.data('modalpopover', null);
            prevClickedElem = null;
		}
	})

})(window.jQuery);