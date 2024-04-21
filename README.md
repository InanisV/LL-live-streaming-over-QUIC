# LL-live-streaming-over-QUIC

This is the main GitHub repository of "LL-live-streaming-over-QUIC".

The repository includes the following:

**./dash-ll-server-aioquic**

This folder contains the author's modified dash server. The server is written in python and uses the aioquic third-party library to implement http3 server. It implements the http3 form to provide mpd video push streaming service.

**./dash-ll-server-quic-go**

This folder contains the dash server rewritten in the go language. Similar to the previously mentioned *dash-ll-server-aioquic*, it is implemented with the auic-go third-party library.

**./dash.js**

This folder contains the author's modified dash.js samples. The author has the ability to obtain the necessary test data from the front-end by modifying the front-end content. The changes were made in `./samples/low-latency/testplayer` .

*The authors would like to emphasize that the initial version of the above content is derived from open source software. Credit will be given to `NUStreaming` and `Dash-Industry-Forum`.*

+ https://github.com/NUStreaming/LoL-plus
+ https://github.com/Dash-Industry-Forum/dash.js

**./py-script**

This folder contains all post-processing scripts, including simple data cleaning and plotting scripts.

### How to Use?


### dash.js
Since the author doesn't know much about front-end, he only made simple changes to `dash.js`. The way to start the modified samples in `dash.js` is the same as in the official version. So I won't repeat it here. Please refer to the official documentation : https://github.com/Dash-Industry-Forum/dash.js.

### dash-ll-server-aioquic
Start the related services in the same way as before.

However, the authors have provided a more convenient way to do so. A docker image for this service is available on DockerHub. It is easy to start the service quickly via docker.

+ 

### dash-ll-server-quic-go

The command to start this service is:
`go run main.go -p 9001 media`

For your convenience, the author has also provided a Docker image. The image is available at the following address.

+ 

## License

This repository follows the MIT License. In case of conflict with other open source License or local regulations, local regulations or open source License shall prevail.