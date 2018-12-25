# Development Notes

This widget start as a adaptation of the original [brat annotation tool](http://brat.nlplab.org) to the development environment of the Jupyter Notebooks. In this document you can find some details of the process.


## Initial hacking:

The original project of brat is a little bit outdated and it's not compatible with the architecture of typical ipython widget.
In order to speed up the process the initial steps were made using a massive search and replace based on the following regular expressions.

- The regex `\$\('#([a-zA-Z_0-9\-]+)'\)` was used to find all the calls to JQuery that look for a specific element in the DOM. And the regex `\$\('#' \+ base_id \+ '_$1'\)` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `\$\('#' \+ base_id \+ '_([a-zA-Z_0-9\-]+)'\)`.
- The regex `id="([a-zA-Z_0-9\-]+)"` was used to find all the ids in the brat DOM embedded in the widget. And the regex `id="\{base_id\}_$1"` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `id="\{base_id\}_([a-zA-Z_0-9\-]+)"`.
- The regex `for="([a-zA-Z_0-9\-]+)"` was used to find all the referenced ids in the brat DOM embedded in the widget. And the regex `for="\{base_id\}_$1"` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `for="\{base_id\}_([a-zA-Z_0-9\-]+)"`.
- The regex `\$\('#([a-zA-Z_ \.:-\[\]\(\)0-9\-]+)'\)` was used to find all the calls to JQuery that look for a path of several elements in the DOM. The result of this lookup gave 49 occurences in two files. The regex `\$\('#([a-zA-Z_\.:-\[\]\(\)0-9\-]+) ` was used as the lookup expression and `\$\('#' \+ base_id \+ '_$1 ` was used to perform the replacement using PyCharm. The regexes showed before produce more results than the first global lookup expression. To find all the replacements use the following regex: `\$\('#' \+ base_id \+ '_([a-zA-Z_]+) `. After the following was used to select another specific cases `#([a-zA-Z_\.:-\[\]\(\)0-9\-]+)`and `#' \+ base_id \+ '_$1` was used to perform the replacement using PyCharm.
- In order to find the remaining cases where a DOM element is constructed using jQuery, the following regex was used to lookup `(id|for)="([a-zA-Z_0-9\-]+)` and this `$1="' \+ base_id \+ '_$2` was used for replacement.

The result of this process was reported in several text files that can be found in [the root of the project in github](https://github.com/Edilmo/brat-widget).


## Examples of the JSON documents sent to the server:

During the development process is useful to see examples of the json documents exchange between the client (javascript code) and the server (python code). Below there are links to examples of each type of json document used by the widget.

- [Span actions](http://www.jsoneditoronline.org/?id=c11d7be261c2f507f15ea9733e927d38)
- [Arc actions](http://www.jsoneditoronline.org/?id=dcac7fd71ec6f3716ba9f0265cb399ff)
- [Other actions](http://www.jsoneditoronline.org/?id=dcac7fd71ec6f3716ba9f0265cbc464a)
