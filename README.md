# instagram mitmproxy addon

* install `mitmproxy`
* configure your browser to point to your local proxy running on port 9091
* run the proxy with `mitmproxy -p 9091 -s instagram.py`
* browse through some instagram accounts, scroll as far as you want data for
* in `mitmproxy` - run the `instadump` command, type `:` to input the command
* you should some `csv` files representing all the data you saw
* if there's any errors and `mitmproxy` doesn't crash - type `E` to go to the event log and look for the red text with the error
