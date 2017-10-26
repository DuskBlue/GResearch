"""Analyse tweets"""
import webhandler

class SentimentAnalyser(object):
    def __init__(self):
        self.negative_words = webhandler.get_negative_words()
        self.neutral_words = webhandler.get_neutral_words()
        self.positive_words = webhandler.get_positive_words()
        self.companies = webhandler.get_company_info()

    def analyse_tweet(self, tweet):
        """Analyse a tweet, extracting the subject and sentiment"""
        sentiment = 0
        company = self.companies[0].name
        negation = False

        for word in tweet.split(" "):
            if word in self.positive_words:
                sentiment = sentiment + 1
            if word in self.negative_words:
                sentiment = sentiment - 1
            for companyObj in self.companies:
                if word == companyObj.name:
                    company = companyObj.name
            if word == "not":
                negation = not negation

        if negation:
            sentiment *= -1
        return [(company, sentiment)]
