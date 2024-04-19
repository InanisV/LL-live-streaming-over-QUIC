# LL-live-streaming-over-QUIC

This is the main GitHub repository of "LL-live-streaming-over-QUIC".

The repository includes the following：

**./dash-11-server-aioquic**

This folder contains the author's modified dash server. The server is written in python and
uses the aioquic third-party library to implement http3 server. It implements the http3 form
to provide mpd video push streaming service.

**./dash-11-server-quic-go**

This folder contains the dash server rewritten in the gO Language. Similar to the previously
mentioned *dash-11-server-aioquic*， it is implemented with the quic-go third-party Library.

**./dash.js**

This folder contains the author's modified dash. js samples. The author has the ability to
obtain the necessary test data from the front-end by modifying the front-end content. The
changes were made in `. / samp les/low-latency/testplayer`

*The authors would like to emphasize that the initial version of the above content is derived
from open-source software. Credit will be given to `NUStreaming` and `Dash-Industry-Forum`.*

+ https://github. com/NUStreaming/LoL-plus
+ https://github. com/Dash-Industry-Forum/dash. js

**./py-script**

This folder contains all post-processing scripts, including simple data cleaning and plotting
scripts.

### How to Use？
### dash.js
The way to start the modified samples in dash.js is the same as in the official version. So
Please refer to the official documentation
https://github.com/
Dash-Industry-Forum/dash.js.

### dash-11-server-aioquic
Start the related services in the same way as before.
However, the authors have provided a more convenient way to do so. A docker image for this
service is available on DockerHub. It is easy to start the service quickly via docker.
