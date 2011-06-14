// Portions and the whole copyright 2009 James Vasile <james@hackervisions.org>
// Released under AGPLv3 <http://www.fsf.org/licensing/licenses/agpl-3.0.html>

var Feed = new Array();
var add_feed_btn = document.images["AddFeedBtn"];

function set_focus(id) { document.getElementById(id).focus(); }

function new_feed(section, url, name, face, faceurl, facewidth, faceheight) {
    var f = new Array();
    f['section'] = section;
    f['feedurl'] = url;
    f['name'] = name;
    f['face'] = face;
    f['faceurl'] = faceurl;
    f['facewidth'] = facewidth;
    f['faceheight'] = faceheight;

    Feed.push(f);
}

function hide_by_id(id) {
    //safe function to hide an element with a specified id
    if (document.getElementById) { // DOM3 = IE5, NS6
	document.getElementById(id).style.display = 'none';
    } else {
	if (document.layers) { // Netscape 4
	    document.id.display = 'none';
	} else { // IE 4
	    document.all.id.style.display = 'none';
	}
    }
}

function addEvent(obj, evType, fn){
    if (obj.addEventListener){
	obj.addEventListener(evType, fn, true);
	return true;
    } else if (obj.attachEvent){
	var r = obj.attachEvent("on"+evType, fn);
	return r;
    } else {
	return false;
    }
}


function render_face_cell(idx){
    var facecell = document.createElement("td");
    facecell.setAttribute('style', 'vertical-align:middle');

    Feed[idx]['feedimg'] = document.createElement("img");
    if (Feed[idx]['faceurl']) {
	Feed[idx]['feedimg'].src = Feed[idx]['faceurl'];
	if (Feed[idx]['facewidth']) {Feed[idx]['feedimg'].width = Feed[idx]['facewidth'];}
	if (Feed[idx]['faceheight']) {Feed[idx]['feedimg'].height = Feed[idx]['faceheight'];}
    } else {
	Feed[idx]['feedimg'].src = "/pub.d/images/silhouette2.png"; // silhouette2.png from http://www.flickr.com/photos/n-o-n-o/3502226571
    }

    facecell.appendChild(Feed[idx]['feedimg']);
    return facecell;
}

function feed_cell_label_input(idx, key, label_text) {
    /// return a label and an input for feed cell data
    var cell = document.createElement("div");
    var label = document.createElement('label');
    label.setAttribute('for', key+idx);
    label.appendChild(document.createTextNode(label_text + ':'));

    var input = document.createElement('input');
    input.type ='text';
    input.name = key + idx;
    input.id = key + idx;
    input.setAttribute('value', Feed[idx][key]);
    input.size = 40;
    input.onchange = function() {Feed[idx][key]=input.value;}

    if (key=='name') {
	var anchor = document.createElement('a');
	anchor.href="javascript:rm_feed(" + idx + ")";

	var rm = document.createElement('img');
	rm.src = "/pub.d/images/rm-feed.png";
	rm.setAttribute('class', "feedbtn");

	anchor.appendChild(rm)
	cell.appendChild(anchor);
	cell.appendChild(document.createTextNode('\u00A0\u00A0')); //&nbsp;
    }

    cell.appendChild(label);
    cell.appendChild(document.createElement("br"));
    cell.appendChild(input);
    cell.appendChild(document.createElement("br"));
    cell.appendChild(document.createElement("br"));
    return cell;
}

function render_hidden(name, value) {
    var hidden = document.createElement('input');
    hidden.type ='hidden';
    hidden.name = name;
    hidden.id = name;
    hidden.setAttribute('value', value);
    return hidden;
}

function render_feed_cell(idx) {
    // returns a td object for feed url and name
    var cell = document.createElement("td");
    cell.id = "feedcell"+idx;
    cell.setAttribute('style', 'text-align: left; float:right; font-weight: bold');

    // The section identifies which part of the config.ini this cell applies to
    // We can't just id by feed url because that might change
    if (Feed[idx]['section']) {
	cell.appendChild(render_hidden('section'+idx, Feed[idx]['section']));
    } else {
	cell.appendChild(render_hidden('section'+idx, 'section'+idx));
    }
    cell.appendChild(render_hidden('delete'+idx, '0'));


    cell.appendChild(feed_cell_label_input(idx, 'name', 'Feed Name'));
    cell.appendChild(feed_cell_label_input(idx, 'feedurl', 'Feed URL'));
    cell.appendChild(feed_cell_label_input(idx, 'faceurl', 'Image URL'));

    return cell;
}

function render_feed_row(idx) {
    // Render one row of the table holding feed info
    var row = document.createElement("tr");
    row.className = 'face'+(idx % 2);
    row.id = "feed_row"+idx;
    row.appendChild(render_face_cell(idx));
    row.appendChild(render_feed_cell(idx));
    return row;
}

function prependChild(parent, node) {
    parent.insertBefore(node, parent.firstChild);
}

function render_feed_rows() {
    var tbl = document.createElement('table');
    tbl.setAttribute('id', 'feed_table');
    var tbody = document.createElement('tbody');
    tbody.setAttribute('id', 'feeds_tbody');
    feed_div = document.getElementById('feeds');
    for (a=0; a<Feed.length; a++) { prependChild(tbody, render_feed_row(a)); }
    tbl.appendChild(tbody);
    feed_div.appendChild(tbl);
}

function rm_feed(idx) {
    // Remove feed
    hide_by_id('feed_row'+idx);
    del = document.getElementById('delete'+idx);
    del.setAttribute('value', '1');
}

function add_feed() {
    // place an additional feed row on the page
    new_feed('','','','','','','');
    prependChild(document.getElementById('feeds_tbody'), render_feed_row(Feed.length-1));
    set_focus('name'+(Feed.length-1));
}


addEvent(window, 'load', function() {
	//render_feed_rows();
	document.getElementById('PlanetName').focus();
});
