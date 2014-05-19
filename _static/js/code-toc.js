$(document).ready(function (){
	var createList = function(selector){
		var ul = $('<ul class="nav nav-normal">');
		var selected = $(selector);

		if (selected.length === 0){
			return;
		}

		selected.each(function (i,e){
			var p = $(e).children('.descclassname');
			var n = $(e).children('.descname');
			var l = $(e).children('.headerlink');

			var name = n.text();
			if(!checkName(name)) {
				return;
			}

			var id = l.attr('href').replace('#','').replace(/\./g, '_');
			var m = $(e).parent();
			m.attr('id', id).prepend('<a name="' + id + '"></a>');

			var a = $('<a>');
			a.attr('href','#' + id).attr('title', 'Link to this definition');

			a.append(p).append(name);

			var entry = $('<li>').append(a);
			ul.append(entry);
		});
		return ul;
	}

	var checkName = function(name) {
		var group_re = /^([a-z]+)s$/;
		if(name.match(group_re)) {
			return true;
		}
		return false;
	}

	var $methodLeaf = $('a[href=#instance-methods].reference.internal:first').parent('li')

	var x = [];
	// x.push(['Classes','dl.class > dt']);
	x.push(['Methods','dl.method > dt']);

	x.forEach(function (e){
		var l = createList(e[1]);
		if (l) {
			$methodLeaf.append(l);
			min = 0;
			max = 100000;
			var methodLeafID = 'leaf' + Math.ceil(Math.random() * (max - min) + min);
			$methodLeaf.attr('id', methodLeafID);
			$('body').scrollspy({ target: '#' + methodLeafID });
			// var ul = c.clone()
			// 	.append('<p class="rubric">'+e[0]+'</p>')
			// 	.append(l);
		}
		// customIndex.append(ul);
	});

});