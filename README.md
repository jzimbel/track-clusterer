# Track Clusterer

Cluster your Spotify tracks using their audio features.

## Usage

You will need Python 2.7, the `pip` package manager, and `git`.
Virtualenvs will also help.

1. Make a virtualenv for the project. (Optional)  
   ```$ mkvirtualenv track-clusterer```
2. Go to the directory of the project, and install dependencies.  
   ```$ cd track-clusterer```  
   ```$ pip install -r requirements.txt```
3. Now you need to grab your Spotify ID.
   Open Spotify and click on your name at the top right. Click the "..." menu
   under your name in the page that loads, and select "Copy Profile Link".
   Paste this somewhere and copy the part
   after the last `/`. If you signed up through Facebook, this is just a number.  
   ```https://open.spotify.com/user/128300609```  
   ```____________________this part ^^^^^^^^^```
4. Run the project with your own track features, or use the provided sample features.  
   ```$ python app.py $YOUR_SPOTIFY_ID -o clusters.json``` OR  
   ```$ python app.py $YOUR_SPOTIFY_ID -i features-jon.json -o clusters.json```
5. A browser tab will open up and Spotify will check if you're okay with giving
   the program some permissions for your account.
   If you are, click 'Okay'.
6. You'll get redirected to Google, but if you look at your browser's URL bar,
   you'll see a huge query string after '.com'. Copy the WHOLE link, as in, 'select all'+'copy',
   and paste this into your terminal.
7. You're done! Wait a few seconds for the results to be printed to clusters.json.
