# SLCB Channel Point Rewards

This script allows the user to add up to 10 Twitch channel point rewards to trigger various different types of events.

## Installing

This script was built for use with Streamlabs Chatbot.
Follow instructions on how to install custom script packs at:
https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts

Click [Here](https://github.com/Encrypted-Thoughts/SLCB-ChannelPointsSFXTrigger/blob/master/ChannelPointsSFXTrigger.zip?raw=true) to download the script pack.

This script requires an oAuth token with access sufficient to read channel point reward redemptions. <br />
It is currently configured function via Authorization Code flow using an application on dev.twitch.tv that you will need to create.
https://dev.twitch.tv/console/apps/create

For the OAuth Redirection URL feel free to use mine: https://et-twitch-auth.com/ <br />
This will just act as a return page that'll display your authorization code that can be entered into the script setting later to get an oAuth token.

Example Application:
![image](https://user-images.githubusercontent.com/50642352/86069644-2c2c5e80-ba40-11ea-80d3-b737422a0003.png)

Once you've setup your twitch application. Retrieve your applications Client ID and generate a Client Secret. These are highlighted in red in the image above.

WARNING: Do not share your Client Secret with anyone as with the combination of your Client Id and Client Secret they'll have permissions to generate oAuth tokens for whatever purpose they want to manipulate your account.

Enter them into the script's corresponding Twitch Auth settings, scroll to the bottom of the settings and Save.
![image](https://user-images.githubusercontent.com/50642352/86070799-2edc8300-ba43-11ea-8a0c-9ee9f87eadeb.png)

Then click the "Get Token" button. This should direct you to a link to retrieve an auth code.
![image](https://user-images.githubusercontent.com/50642352/86070427-4f580d80-ba42-11ea-862e-3f188e7012d4.png)

If you used my redirect url you should end up at a page that looks something like this:
![image](https://user-images.githubusercontent.com/50642352/86070889-65b29900-ba43-11ea-8528-31e3ee936b23.png)

Copy the Authorization Code from this page into the script settings shown above and once again scroll to the bottom of settings and Save. <br />
Congrats now the script should be able to run and maintain authentication by itself. (It will refresh  it's authenication roughly every 4 hours if the bot is left running.)

If for some reason it ever loses authenication you can manually renew the auth code by clicking the "Delete Saved Tokens" then clicking the "Get Token" button and redoing the above steps.

## Use

Once installed you just need to add custom channel point rewards to your twitch channel and then match the names of the reward to a Twitch Reward event in the script settings.

You will also need to select the activation type and reward type.

Activation Type is when the reward will be triggered. Either immediately at redemption or when it is Accepted/Removed from the reward queue.
Note: Currently I know of know way of distinguishing between an event being removed or accepted from the queue based on the events twitch broadcasts. So removing the item from the reward queue will still trigger the event.

Currently there are 5 different Reward Types available.

#### Alert

#### Countdown

#### Timeout User

#### Currency Exchange

#### AutoHotKey

## Author

EncryptedThoughts - [Twitch](https://www.twitch.tv/encryptedthoughts)

## References

This script makes use of TwitchLib's pubsub listener to detect the channel point redemptions. Go check out their repo at https://github.com/TwitchLib/TwitchLib for more info.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


