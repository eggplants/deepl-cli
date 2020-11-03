#!/bin/bash

# translate a page content in English into Japanese
curl -s http://example.com/ | grep -oP '(?<=>)[^<]+' | deepl en:ja

# translate the article page about LOD written by TBL
curl -s https://www.w3.org/DesignIssues/LinkedData.html |
    tr -d \\n | grep -oP -m1 '(?<=p>)[^<]+(?=</p>)' |
    head -3 | sed 's/&nbsp;/ /g' | deepl :ja
