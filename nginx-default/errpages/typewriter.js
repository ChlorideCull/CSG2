typewrite_locked = false;
typewrite_sounds = [
	'remington_5.mp3',
	'remington_6.mp3',
	'remington_7.mp3',
	'remington_10.mp3'
];
typewrite_sounds_db = {};

for (var i = 0; i < typewrite_sounds.length; i++) {
	typewrite_sounds_db[typewrite_sounds[i]] = [
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i]),
		new Audio(typewrite_sounds[i])
	]
}

function _typewrite(str, curelem) {
	typewrite_locked = true;
	var iterfunc = function(i, elem) {
		if (i == str.length) {
			typewrite_locked = false;
			return;
		}
		var sndname = typewrite_sounds[Math.floor(Math.random() * typewrite_sounds.length)];
		typewrite_sounds_db[sndname][Math.floor(Math.random() * typewrite_sounds_db[sndname].length)].play();
		elem.text(elem.text() + str.charAt(i));
		setTimeout(function() { iterfunc(i+1,elem) }, 150);
	}
	iterfunc(0, curelem);
}

function typewrite(paperbody, strarr, isspecial) {
	if (typewrite_locked) {
		setTimeout(function() { typewrite(paperbody, strarr, isspecial) }, 100);
		return;
	} else {
		if (isspecial === undefined) {
			isspecial = false;
		}
		if (!isspecial) {
			var targetp = $("<p>");
			paperbody.append(targetp);
		} else {
			var targetp = $("<span>");
			paperbody.append(targetp);
		}

		if (strarr[0].constructor === Array) {
			typewrite(targetp, strarr[0], true);
		} else {
			_typewrite(strarr[0], targetp);
		}
		
		if (strarr.length > 1) {
			var newstrarr = [];
			for (var i = 1; i < strarr.length; i++) {
				newstrarr[i-1] = strarr[i];
			}
			if (isspecial) {
				paperbody.append($("<br>"));	
			}
			setTimeout(function() { typewrite(paperbody, newstrarr, isspecial) }, 100);
		}
	}
}