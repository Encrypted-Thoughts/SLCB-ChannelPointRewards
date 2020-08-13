# SLCB Channel Point Rewards

This script allows the user to add up to 10 Twitch channel point rewards to trigger various different types of events.

## Installing

This script was built for use with Streamlabs Chatbot.
Follow instructions on how to install custom script packs at:
https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts

Click [Here](https://github.com/Encrypted-Thoughts/SLCB-ChannelPointsSFXTrigger/blob/master/ChannelPointsSFXTrigger.zip?raw=true) to download the script pack.

You will need to give the script access to broadcast streamlabs events. This can be achieved by right clicking on the script in Streamlabs Chatbot and selecting "Insert API Key". https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Script-overlays

![api key](https://user-images.githubusercontent.com/50642352/83985340-7701fd00-a8fe-11ea-9aca-393d6dc7d4b4.png)

After that you should be able to add a new Browser source in OBS and point it to "index.html" located in the "overlay" folder in the script folder. If you're unsure how to locate the streamlabs custom scripts folder you can select "Open Script Folder" shown in the above step.

![index](https://user-images.githubusercontent.com/50642352/83985548-48d0ed00-a8ff-11ea-94f8-0e56c4f42d64.png)

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


