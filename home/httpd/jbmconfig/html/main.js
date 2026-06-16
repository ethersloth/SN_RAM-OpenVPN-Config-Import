(function () {
var requirejs_paths = {
	biginteger:'js/lib/biginteger',
	bignumber:'js/lib/bignumber-4.0.1.min',
	GauWeb:'js/GauWeb',
	pako:'js/lib/pako-1.0.3.min',
	toastr:'js/lib/toastr-2.1.3.min',
	validate:'js/validate',
	ValidationManager:'js/ValidationManager',
	CellularProperties:'js/CellularProperties',
	jquery:'js/lib/jquery-1.11.1.min',
	'jquery-ui':'js/lib/jquery-ui-1.10.3.custom',
	'jquery.form':'js/lib/jquery.form',
	bootstrap:'js/lib/bootstrap.min',
	knockout:'js/lib/knockout-3.2.0',
	'knockout-jqueryui':'js/lib/knockout-jqueryui-v0.7.1.min',
	pager:'js/lib/pager-1.0.1.min'
}
if (document.md5link_paths) {
	var md5Keys = Object.keys(document.md5link_paths);
	for (var z = 0; z < md5Keys.length; z++) {
		requirejs_paths[md5Keys[z]] = document.md5link_paths[md5Keys[z]];
	}
}
requirejs.config({
	baseUrl: '/',
	waitSeconds: 0, // Disable timeout for loading modules
	shim: {
		bootstrap: ['jquery'],
		pager: ['jquery', 'knockout'],
		'jquery.form': ['jquery'],
		'jquery-ui': ['jquery'],
		'knockout-jqueryui': ['jquery', 'knockout', 'jquery-ui'],
		hashchange: ['jquery']
	},
	paths: requirejs_paths
});
})();

require(['jquery', 'knockout', 'pager', 'ValidationManager', 'GauWeb', 'jquery-ui', 'knockout-jqueryui','bootstrap'], function ($, ko, pager, ValidationManager, GauWeb) {
	// Bootstrap 2 fix for "Maximum call stack size exceeded" for multiple modals
	$.fn.modal.Constructor.prototype.enforceFocus = function () {};
	// Add filter to find elements that do not appear on-screen
	// http://stackoverflow.com/questions/8897289/how-to-check-if-an-element-is-off-screen
	$.expr.filters.offscreen = function(element) {
		var rect = element.getBoundingClientRect();
		return (
			(rect.left + rect.width) < 0
			|| (rect.top + rect.height) < 0
			|| (rect.left > window.innerWidth || rect.top > window.innerHeight)
		)
	}
	$.expr.filters.onscreen = function(element) {
		var rect = element.getBoundingClientRect();
		return (
			(rect.left + rect.width) >= 0
			&& (rect.top + rect.height) >= 0
			&& (rect.left <= window.innerWidth && rect.top <= window.innerHeight)
		)
	}
	/**
	 * Autocomplete from list specified in autocomplete: list
	 */
	ko.bindingHandlers.autocomplete = {
		init: function (element, valueAccessor, allBindingsAccessor) {
			if (! allBindingsAccessor().hasOwnProperty("value")) {
				throw "autocomplete binding needs a value to set"
			}
		},
		update: function (element, valueAccessor, allBindingsAccessor) {
			$(element).autocomplete({
				source: ko.utils.unwrapObservable(valueAccessor()),
				select: function (evt, ui) {
					// Override select to set observable - avoids having to wait for de-select event
					allBindingsAccessor().value(ui.item.value)
				}
			})
		}
	}
	// Use with data-bind="debug: $data"
	ko.bindingHandlers.debug = {
		init: function (element, valueAccessor) {
			console.log('Binding Debug:');
			console.log(element);
			console.log(valueAccessor());
		}
	}
	ko.bindingHandlers.draggable = {
		init: function (element) {
			$(element).draggable();
			$(element).css("cursor", "move");
		}
	}
	/**
	 * Present File object from drag-and-drop events
	 *
	 * @example
	 * // calls func with File object on drop event
	 * <element data-bind="fileDrop: func"></element>
	 */
	ko.bindingHandlers.fileDrop = {
		init: function (element, valueAccessor) {
			ko.utils.registerEventHandler(element, "dragover", function (evt) {
				evt.preventDefault()
				$(element).css("background-color", "#ffffc2")
			})
			ko.utils.registerEventHandler(element, "dragleave", function (evt) {
				evt.preventDefault()
				$(element).css("background-color", "#fff")
			})
			ko.utils.registerEventHandler(element, "drop", function (evt) {
				evt.preventDefault()
				$(element).css("background-color", "#fff")
				var file = null
				try {
					file = evt.originalEvent.dataTransfer.files[0]
				}
				catch (e) {
					console.log("Could not find file in event")
				}
				if (file) {
					valueAccessor()(file)
				}
			})
			// dragover will prevent the drop event from firing
			ko.utils.registerEventHandler(element, "dragover", false)
		}
	}
	/**
	 * Present File object from file selection event
	 *
	 * @example
	 * // calls func with File object after user selects from the browser
	 * <input type="file" data-bind="fileOnChange: func"></input>
	 */
	ko.bindingHandlers.fileOnChange = {
		init: function (element, valueAccessor) {
			ko.utils.registerEventHandler(element, "click", function (evt) {
				// Clear file until something is selected
				valueAccessor()(null)
				$(element)[0].value = ""
			})
			ko.utils.registerEventHandler(element, "change", function (evt) {
				valueAccessor()( $(element)[0].files[0] )
			})
		}
	}
	ko.bindingHandlers.help = {
		init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
			$(element).click(function () {
				GauWeb.getHelp(
					$(this),
					ko.utils.unwrapObservable(valueAccessor().link),
					ko.utils.unwrapObservable(valueAccessor().title)
				)
			});
		}
	}
	/**
	 * Binds modal visibility to an observable for logical control and subscriptions
	 * @example
	 * // Binds javascript object to modal
	 * this.myModal = {visible: ko.observable(false)}
	 * <div id="exModal" data-bind="modal: myModal" class="hide"></div>
	 * @example
	 * // Clear field when modal disappears
	 * this.myModal.visible.subscribe(function () {this.otherField.clear()}, this)
	 */
	ko.bindingHandlers.modal = {
		init: function (element, valueAccessor) {
			$(element).addClass("modal")
			var mobj = valueAccessor()
			if (! ko.isObservable(mobj.visible)) {
				throw "modal binding requires visible observable"
			}
			mobj.visible.subscribe(function (visible) {
				if (visible) {
					$(element).modal("show")
				}
				else {
					$(element).modal("hide")
				}
			})
			$(element).on("shown", function () {
				mobj.visible(true)
			})
			$(element).on("hidden", function () {
				mobj.visible(false)
			})
		}
	}
	ko.bindingHandlers.slider = {
		init: function (element, valueAccessor, allBindingsAccessor) {
			var options = allBindingsAccessor().sliderOptions || {};
			$(element).slider(options);
			ko.utils.registerEventHandler(element, "slide", function (event, ui) {
				var observable = valueAccessor();
				observable(ui.value);
			});
			ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
				$(element).slider("destroy");
			});
		},
		update: function (element, valueAccessor) {
			var value = ko.utils.unwrapObservable(valueAccessor());
			if (isNaN(value)) value = 0;
			$(element).slider("value", value);
		}
	}
	ko.bindingHandlers.tabbable = {
		init: function (elm, va) {
			// Since this only runs on init, shouldn't pass an observable. But just in case, unwrap
			if (ko.utils.unwrapObservable(va()) === false) {
				return;
			}
			$(elm).keydown(function(e) {
				if(e.keyCode === 9) { // tab was pressed
					// get caret position/selection
					var start = this.selectionStart;
					var end = this.selectionEnd;

					var $this = $(this);
					var value = $this.val();

					// set textarea value to: text before caret + tab + text after caret
					$this.val(value.substring(0, start)
								+ "\t"
								+ value.substring(end));

					// put caret at right position again (add one for the tab)
					this.selectionStart = this.selectionEnd = start + 1;

					// prevent the focus lose
					e.preventDefault();
				}
			});
		}
	}

	function checkForCorruption () {
		var nocr = "nocr";
		// If we clicked one of the links below to get here, we don't want to re-show the alert
		if (window.location.href.match(nocr)) {
			return;
		}
		// Alert if ENV2_FLAG_CORRUPT is present
		GauWeb.utils.postForJSON("cgi-bin/corrupt.cgi", {query:"check"}, function (res) {
			var body = "It appears your configuration may have become out of sync with how your device is behaving due to a recent upgrade. Please visit the following pages to confirm your device is configured correctly";
			if (res.corrupt) {
				body += '<br /><i>(links will open in a new tab)</i><br />';
				// Append a special GET query parameter to the end so we can hide this dialog
				// for subsequent tabs
				if (res.corrupt.match("iptrans"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/iptrans?'+nocr+'">IP Transparency</a>';
				if (res.corrupt.match("fwgeneral"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/fwgeneral?'+nocr+'">Firewall</a>';
				if (res.corrupt.match("dhcpserver"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/dhcpserver?'+nocr+'">DHCP Server</a>';
				if (res.corrupt.match("switchctl"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/switchctl?'+nocr+'">Switch Control</a>';
				if (res.corrupt.match("svmclient"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/svm?'+nocr+'">SVM</a>';
				if (res.corrupt.match("gps"))
					body += '<a style="margin: 5px" class="btn" target="_blank" href="#!/gps?'+nocr+'">GPS</a>';
				GauWeb.confirm({
					title: "WARNING",
					body: body,
					ifCancel: function () {GauWeb.utils.postForJSON("cgi-bin/corrupt.cgi", {query:"set"})},
					cancelText: "Clear this warning",
					okText: "Remind me later"
				});
			}
		});
	}

	$(document).ready(function () {
		GauWeb.idleInterval = setInterval(function () {
			GauWeb.idleTime(GauWeb.idleTime() + 10);
		}, 10000);
		$(this).mousemove(function (e) {
			GauWeb.idleTime(0);
		});
		$(this).keypress(function (e) {
			GauWeb.idleTime(0);
			// Ignore keypress if enter key is used on not-link
			if (e.keyCode == 13 && ('button' !== e.target.localName && 'a' !== e.target.localName && 'textarea' !== e.target.localName)) {
				return false;
			}
		});
		GauWeb.loader.show("Loading Model Profile");
		$('#JsPlaceholder').hide();
		GauWeb.loadModelProfile(function () {
			// model profile includes custom pages. Setting up pager now means
			// we can handle navigating to a custom page on our initial load.
			pager.Href.hash = '#!/';
			pager.extendWithPage(GauWeb);
			ko.applyBindings(GauWeb, $('#wrap')[0]);
			pager.start();
			checkForCorruption();
			GauWeb.loader.hide();
		});
		$.ajax({
			url: "https://redlion.atlassian.net/s/d41d8cd98f00b204e9800998ecf8427e/en_US-7jch19-1988229788/6144/177/1.4.0-m6/_/download/batch/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector-embededjs/com.atlassian.jira.collector.plugin.jira-issue-collector-plugin:issuecollector-embededjs.js?collectorId=e0031d12",
			type: "get",
			cache: true,
			dataType: "script"
		});
	});
});
