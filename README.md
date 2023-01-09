qbittorrent-plugins
-------------------
A repository holding the qBittorrent plugins I've written.

### nCore

This qBittorrent search plugin allows you to search for torrents directly on nCore and download them easily into your qBittorrent client.

It requires an active nCore account, which is only achievable through an invitation!

# Installation

* First, download the **ncore.py** plugin from [here](https://raw.githubusercontent.com/darktohka/qbittorrent-plugins/master/ncore.py). Right click on the script and use your browser's **Save as...** feature.
* Open the **ncore.py** file for editing using a text editor of your choice, such as Notepad++.
* Look for the line containing **EDIT YOUR CREDENTIALS HERE**, usually on line 50.
* Introduce your nCore username and password on the following two lines, respectively. Replace `your_username` and `your_password` with the correct values.
* If you are using 2 factor authentication, you should replace `enter_code` with your code, and then quickly follow the next steps, before the code expires.
* Open qBittorrent, enable the search engine using `Views > Search Engine`, then open the Search tab.
* Press the `Search plugins...` button in the lower right corner, then finally press the `Install a new one` button.
* Press the button labeled as `Local file` and choose the **ncore.py** plugin you've completed with your username and password.
* Your plugin should now be installed! Feel free to switch between search categories at any time.

# Sorting by newest

By default, this plugin will search nCore using keywords. If you want to list the newest torrents, choose your category and simply search for a dot: `.`

# Caveats

Attempting to log into nCore with an invalid username or password will trigger nCore's Google Captcha system. After logging in with invalid credentials, no further attempts will be possible until the captcha system deactivates. This takes around 5 minutes after each attempt.

In other words, if you run into the following error: *Could not log in. Your credentials are invalid! Please wait 5 minutes between attempts*, do NOT attempt to spam search requests! Instead, double-check your credentials and wait a few minutes before trying again.
