"""This is the main module"""
import random
import webhandler
import sentimentanalyser

def main():
    """Run client"""
    if not webhandler.API_KEY:
        raise ValueError("Set your API_KEY in webhandler.py! Find it on https://devrecruitmentchallenge.com/account")

    analyser = sentimentanalyser.SentimentAnalyser()

    print("Getting challenge list")
    challenge_list = webhandler.get_challenge_list()
    print("There are {} challenges".format(len(challenge_list)))

    for info in challenge_list:
        print("Solving challenge {} - {}".format(info.cid, info.challenge_type))
        challenge = webhandler.get_challenge(info.cid)

        if info.challenge_type == "pertweet":
            handle_pertweet(challenge, analyser)
        elif info.challenge_type == "aggregated":
            handle_aggregated(challenge, analyser)
        else:
            print("Unrecognised challenge type '{}'".format(info.challenge_type))

def handle_pertweet(challenge, analyser):
    """Handle a per-tweet challenge"""
    sentiments = {}
    for tweet in challenge.tweets:
        sentiment_list = analyser.analyse_tweet(tweet.tweet)
        sentiments[tweet.tid] = [{'subject': subject, 'sentiment': sentiment} 
                                 for (subject, sentiment) in sentiment_list]
    submission = {'challengeId': challenge.info.cid, 'perTweetSentiment': sentiments}
    result = webhandler.post_pertweet_submission(submission)
    print("Mark = {}%".format(result.mark))

def handle_aggregated(challenge, analyser):
    """Handle an aggregated challenge"""
    sentiments = {}
    # Just guess
    min_time = min(t.time for t in challenge.tweets)
    max_time = max(t.time for t in challenge.tweets) + 1
    companies = webhandler.get_company_info()
    known_subjects = []

    for company in companies:
        known_subjects.append(company.name)

    subject_sentiments = {}

    for subject in known_subjects:
        subject_sentiments[subject] = {}
        for i in range(min_time, max_time):
            subject_sentiments[subject][i] = []

    print(subject_sentiments)

    for tweet in challenge.tweets:
        tweet_analysis = analyser.analyse_tweet(tweet.tweet)
        for (subject, sentiment) in tweet_analysis:
            subject_sentiments[subject][tweet.time].append(sentiment)

    print(subject_sentiments)

    for subject, times in subject_sentiments.items():
        sentiments[subject] = {}
        useSubject = False
        for time, scores in times.items():
            length = 0
            total = 0
            for score in scores:
                useSubject = True
                length += 1
                total += score
            try:
                sentiments[subject][time] = total / length
            except ZeroDivisionError:
                sentiments[subject][time] = 0
        if not useSubject:
            del sentiments[subject]

    # for subject in known_subjects:
    #     subject_sentiments = {}
    #     for i in range(min_time, max_time):
    #         subject_sentiments[i] = random.randrange(-1, 1)
    #     sentiments[subject] = subject_sentiments

    submission = {'challengeId': challenge.info.cid, 'sentiments': sentiments}
    print(submission)
    result = webhandler.post_aggregated_submission(submission)
    print ("Mark = {}%".format(result.mark))

if __name__ == "__main__":
    main()
