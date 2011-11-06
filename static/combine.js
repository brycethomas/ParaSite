function combine(text) {
    console.log("entered combine()");
    var lines = jQuery.trim(text).split("\n");
    if (lines == "") {
	return "";
    }
    var wordCounts = new Object(); // key: word, value: number of occurences
    for(var i=0; i < lines.length; i++) {
	var word = lines[i].split(" ")[0]
	var wordCount = lines[i].split(" ")[1]
	if (!(word in wordCounts)) { // set to 0 first time we see AP
	    wordCounts[word] = 0;
	}
	wordCounts[word] += parseInt(wordCount);
    }
    output = "";
    for (word in wordCounts) {
	output += word + " " + wordCounts[word] + "\n";
    }
    console.log(output);
    console.log("exiting combine()");
    return output;
}