# Vidhash
[Vidhash](https://pypi.org/project/vidhash/) is a perceptual video hashing and checking library, to detect similar videos, or videos containing similar scenes.

## How it works
Basically, this video hashing works by scaling the video down a bit, and taking 5 frames a second as images, and performing image hashes on those frames.
Then it can do checks by checking how many image hashes from one video match up with image hashes from another.

## How to use
This documentation is a little sparse at the moment, but the basic summary is that to hash a video, use `video_hash = hash_video(video_path)`.  
This returns a `VideoHash` object.  
You can also provide a `HashSettings` object. HashSettings need to match for two video hashes to be compared.
Currently HashSettings allow specifying the

When checking video hashes against each-other, use `video_hash.check_match(other_hash)`.
You can optionally provide a `MatchOptions` object as a second argument, or use a MatchOptions object and call the `MatchOptions.check_match(hash1, hash2)` method on it.

There are 3 supported types of MatchSettings:
- `FrameCountMatch`
  - Checks whether a specified number of frames match between the two videos
  - Allows specifying the hamming distance between two frames which should be considered a "match"
  - Allows ignoring blank frames
- `PercentageMatch`
  - Checks whether a specified percentage of the shorter video's frames match the longer video
  - Allows specifying the hamming distance between two frames which should be considered a "match"
  - Allows ignoring blank frames
- `DurationMatch`
  - Checks whether a specified "duration" of frames match up in order between the two videos
    - e.g. 3 seconds duration, at 5 fps, would check whether 15 frames match, in a row, between the two videos
  - Allows specifying the hamming distance between two frames which should be considered a "match"


## Todo
- Code
  - Wrapper for imagehash.ImageHash
  - Datastore
    - (For looking up matching videos from a collection)
- More documentation
- More tests
