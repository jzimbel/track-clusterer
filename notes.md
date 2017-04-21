# Miscellaneous project notes

- Spent a lot of time (probably too much) trying to figure out how to choose a good epsilon value for DBSCAN
  - Tried searching around a bit (https://www.quora.com/How-do-I-choose-value-of-epsilon-in-DBSCAN)
  - Solutions are pretty complicated :c
  - Ended up adding some code to main that tries clustering with a lot of epsilon
    values and measures success on:
    - maximize: % of features placed in a cluster (rather than labelled as noise)
    - maximize: number of clusters
    - minimize: avg. difference in cluster size
  - Picks the best clustering and uses that.
  - https://fivethirtyeight.com/features/spotify-knows-me-better-than-i-know-myself/
    - tl;dr Most people tend to have 2 main clusters:
      - One contains pop and similar music they might be ashamed of listening to
      - The other contains music they tell people they listen to
