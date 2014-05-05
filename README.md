cms-client-sdk-python
==================

Python SDK for Volar's client sdk, Version 2 (pre-alpha)

This is a rework of the existing [Python SDK](https://github.com/volarvideo/cms-client-sdk).  Primary purpose of the rework was to eliminate the step of uploading files directly to the volar servers - instead, when videos are archived or posters are uploaded, the files are uploaded to our remote storage and enqueued for transcode, relieving a lot of the work our servers have to do to bring content to viewers.

The downside is that the Python sdk now has a new dependancy - the Amazon AWS SDK, otherwise known as boto.  However, installation of the boto module is easy - follow the instructions on [https://aws.amazon.com/sdkforpython/](https://aws.amazon.com/sdkforpython/)
