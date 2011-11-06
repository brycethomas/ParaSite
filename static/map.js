function map(MAC, text) {
    console.log("entered map()");
    var output = "";
    // extremely crude method of splitting words
    var words = text.replace(/\W+/g,' ');
    var words = jQuery.trim(words).split(" ");
    //var words = jQuery.trim(text).split(" ");
    for(var i=0; i < words.length; i++) {
	output += words[i] + " 1\n";
    }
    //console.log("map output:\n" + output);
    console.log("exiting map()");
    return output;
}