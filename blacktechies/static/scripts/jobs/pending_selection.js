$(document).ready(function () {
	if (! Backbone) {
		return;
	}

	var listing = Backbone.Model.extend({
		defaults: {
			"title": null,
			"body": null,
		},

		urlRoot: "/jobs/listing",
	});

	var getSelection = function (event){
		console.log(event)
		var selection = document.getSelection();
		if (! selection) {
			return;
		}
		text = selection.toString();
		console.log(text);
		SELECTION = selection;
	};

	if ('getSelection' in document) {
		$(document).on('mouseup', getSelection);
	}
});
