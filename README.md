# Welcome to your AppEngine starter kit

### Setup

[Install Python SDK for Google AppEngine](https://cloud.google.com/appengine/docs/standard/python/download)

```sh
make install
```

### Development

```sh
make server
# your debug server is now running at localhost:8080
```

Run tests:

```sh
make test
```

### Deployment

```sh
make deploy
```

### External libraries

If you add a new external dependency to requirements.xlib.txt you must run the following command and commit:

```sh
make xlib
```