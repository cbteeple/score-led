# score-led
ScoreLED Technology

![Score-LED](https://raw.githubusercontent.com/cbteeple/score-led/master/docs/scoreled.jpg)

## Dependencies:
### Hardware
1. [ScoreLED bases + light panels](https://clarkteeple.weebly.com/lightboxes)
2. Raspberry pi (tested on the Pi 2B+ and 3B+ so far)

### Software
- [tweepy](https://www.tweepy.org/), a python wrapper for the twiter api: `pip install tweepy`
- [textblob](https://textblob.readthedocs.io/en/dev/), a text handing api: `pip install textblob`
- [yaml](https://yaml.org/), yet another markup language: `pip install pyyaml`

## Usage:
### Hardware Setup
1. Connect all four sets of three-pin LED plugs to the GPIO header on the pi

### Software Setup
1. Set up the team names, twitter handles, and LED colors for each team using hex codes in "_settings.yaml_"
2. Set the default thresholds for sentiment colors in "_thresholds.yaml_"

### Run
1. SSH into the pi
2. Start a tmux instance
3. Navigate to the score-led folder
```bash
cd ~/Documents/score-led
```
4. Run the main file
```bash
python main_multithreading2019.py
```
5. To adjust the twiter sentiment thresholds live, exit the tmux instance and use the update command
```bash
python updateThresh.py #1 #2
```
  - #1: negative threshold (default: 50)
  - #2: positive threshold (default: 80)
  - _You must give this command two threshold values_
