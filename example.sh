#!/bin/bash

# translate a page content in English into Japanese
curl -s http://example.com/ | grep -oP '(?<=>)[^<]+' | deepl --fr en --to ja -s

# translate the article page about LOAD written by TBL
curl -s https://www.w3.org/DesignIssues/LinkedData.html |
    tr -d \\n | grep -oP -m1 '(?<=p>)[^<]+(?=</p>)' |
    head -3 | sed 's/&nbsp;/ /g' | deepl --to ja -s

# translate the Announce on Codeforces
curl -s 'https://codeforces.com/blog/entry/84257?locale=ru' |
    grep -m5 ttypography|sed '$!d' | grep -oP '(?<=>)[^<]+' | deepl --fr ru --to en -s
