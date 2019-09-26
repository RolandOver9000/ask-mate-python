/*
 * Search for text in the window ignoring tags
 *
 * Parameters:
 *     text: a string to search for
 *     backgroundColor:
 *         "yellow" for example, when you would like to highlight the words
 *         "transparent", when you would like to clear the highlights
 * */
function doSearch(text, backgroundColor) {
    if (window.find && window.getSelection) {
        document.designMode = "on";
        var sel = window.getSelection();
        sel.collapse(document.body, 0);

        let count = 0;
        while (window.find(text)) {
            if (count > 0) {
            document.execCommand("HiliteColor", false, backgroundColor);
            sel.collapseToEnd(); }
            else {count = count + 1;}
        }
        document.designMode = "off";
    }
}