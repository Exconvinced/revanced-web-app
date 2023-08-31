# ReVanced Web App
### 📢 Test release is [here](https://github.com/exconvinced/revanced-web-app/releases/tag/v0.0.0-dev)!

#### Video Demo:  [ReVanced Web App](https://youtu.be/-MK7L0JYTxU)

#### Description:

A web implementation of the popular [ReVanced](https://github.com/ReVanced)!
Patch your Android apps on a familiar interface with a powerful PC hardware.
Combines the comfortable user experience of the mobile app [ReVanced Manager](https://github.com/revanced/revanced-manager) and the efficiency of the commandline [ReVanced CLI](https://github.com/revanced/revanced-cli).

[![Watch the video](./.preview/thumbnail.png)](https://youtu.be/-MK7L0JYTxU)

#### Specifications

- Built on Flask and Javascript.
- Follows [Tailwind CSS](https://tailwindcss.com/) styling convention.
- Uses [AAPT](https://github.com/exconvinced/aapt) to read and verify APK manifest data.
- Runs [ReVanced](https://github.com/ReVanced) locally with the following components:
  - ReVanced CLI [v2.22.0](https://github.com/ReVanced/revanced-cli/releases/tag/v2.22.0)
  - ReVanced Patches [v2.187.0](https://github.com/ReVanced/revanced-patches/releases/tag/v2.187.0)
  - ReVanced Integrations [v0.117.0](https://github.com/ReVanced/revanced-integrations/releases/tag/v0.117.0)

#### Prerequisites
- [Python 3](https://www.python.org/downloads/release/python-3106/)
- [OpenJDK 11](https://jdk.java.net/archive/)

#### Preview

![image](./.preview/demo.gif)

Full layout             |  Mobile layout
:-------------------------:|:-------------------------:
![image](./.preview/full_new.png)  |  ![image](./.preview/mobile.png)


<!-- #### Prerequisites
Download [Java SDK 11.0.2](https://jdk.java.net/archive/). 
Finally, extract it into `/revanced` directory, then rename the extracted folder as `jdk`.
The complete path for Java should now be `/revanced/jdk/bin/java.exe`. -->


#### Disclaimer
This is not an official app. This app simply utilizes ReVanced in the backend.

#### Motivation

The mobile app is occasionally buggy and slow on some devices,
e.g. the patch process eventually freezes especially upon leaving and returning to the app. 
The CLI option is versatile but non-techy people may find it hard to set up and use.
This project combines the accessibility of the mobile app and the efficiency of CLI.

<details>
<summary><h5>Dedication to CS50</h5></summary>
  I needed to build something for the <a href="https://www.edx.org/course/introduction-computer-science-harvardx-cs50x">CS50</a> final project.
  I completed this project in 3 days, thanks to ChatGPT for helping me troubleshoot errors.
  This is relatively easier than solving the Tideman problem set!
  <br><br>
  I learned a lot about the communication logic between `app.routes` in Flask and `event.sources` in Javascript. 
  I should study proper coding paradigms for writing cleaner code for my next project.
</details>
