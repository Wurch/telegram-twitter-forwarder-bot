from functools import wraps
import re


def with_touched_chat(f):
    @wraps(f)
    def wrapper(bot, update=None, *args, **kwargs):
        if update is None:
            return f(bot, *args, **kwargs)

        chat = bot.get_chat(update.message.chat)
        chat.touch_contact()
        kwargs.update(chat=chat)
        return f(bot, update, *args, **kwargs)

    return wrapper


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def markdown_twitter_usernames(text):
    """Restore markdown escaped usernames and make them link to twitter"""
    return re.sub(r'@([A-Za-z0-9_\\]+)',
                  lambda s: '[@{username}](https://twitter.com/{username})'
                  .format(username=s.group(1).replace(r'\_', '_')),
                  text)


def markdown_twitter_hashtags(text):
    """Restore markdown escaped hashtags and make them link to twitter"""
    return re.sub(r'#([^\s]*)',
                  lambda s: '[#{tag}](https://twitter.com/hashtag/{tag})'
                  .format(tag=s.group(1).replace(r'\_', '_')),
                  text)


def de_emojify(text):
        return text.encode('ascii', 'ignore').decode('ascii')


def simplify_message(text):
    splitted_text = text.split("  ")
    if len(splitted_text) == 2:
        return splitted_text[0]
    elif splitted_text == 1 and "Liquidation" in text:
        splitted_text = text.split(" - ")
        return splitted_text
    else:
        return text
    

def prepare_tweet_text(text):
    """Do all escape things for tweet text"""
    res = de_emojify(text)
    res = simplify_message(res)
    res = escape_markdown(res)
    res = markdown_twitter_usernames(res)
    res = markdown_twitter_hashtags(res)
    return res

def validate_volume(tweet):

    text = tweet.text

    try:
        if tweet.screen_name == "BXRekt":
            x = re.search("[Sell|Buy] (.*) @", text).group(1)
            if "+" in x:
                value = 0
                for number in x.split("+"):
                    value += int(number.replace(",",""))
            else:
                value = int(x.replace(",",""))

            if value >= 5_000:
                return True
            else:
                return False
        elif tweet.screen_name == "whalecalls":
            x = re.search("Liquidation: (.*) contracts", text)
            if x:
                value = x.group(1)
                value = int(value.replace(",",""))
                if value >= 5_000:
                    return True
                else:
                    return False
            elif re.search("Liquidation: (.*) BTC", text) != None:
                x = re.search("Liquidation: (.*) BTC", text).group(1)
                value = float(x.replace(",",""))
                if value >= 1:
                    return True
                else:
                    return False
            else:
                return True
        elif tweet.screen_name == "WhaleBotRektd":
            if "HuobiDM" in text:
                x = re.search("@ (.*):", text).group(1)
                value = int(x.replace(",",""))
                if value >= 5_000:
                    return True
                else:
                    return False
            elif "OKEx" in text:
                x = re.search("[Sell|Buy] \$(.*)", text).group(1)
                value = int(x.replace(",",""))
                if value >= 5_000:
                    return True
                else:
                    return False
            elif "Bybit" in text:
                x = re.search("[Sell|Buy] (.*)", text).group(1)
                value = int(x.replace(",",""))
                if value >= 5_000:
                    return True
                else:
                    return False
            elif "Binance" in text:
                x = re.search("[Sell|Buy] \$(.*)", text).group(1)
                value = int(x.replace(",",""))
                if value >= 5_000:
                    return True
                else:
                    return False
            else:
                return True
    except AttributeError:
        return True


def validate_coins(tweet):

    if tweet.screen_name in ["BXRekt", "whalecalls", "WhaleBotRektd"]:
        text = tweet.text
        print(text)
        if (not "XBT" in text or "XBTUSD" in text) \
            and (not "XRP" in text) \
            and (not "TRX" in text) \
            and (not "ADA" in text) \
            and (text.startswith("Liquidated") or "Liquidation" in text):
            return True
        else:
            return False
    else:
        return True
        

def validate_tweet(tweet):
    
    if validate_volume(tweet) == True and validate_coins(tweet) == True:
        return True
    else:
        return False