import datetime
import json
import time
import urllib
import urllib2


class Match(object):
    def __init__(self, match):
        self.live = match['b_Live']
        self.finished = match['b_Finished']
        self.home_team = match['c_HomeTeam_en']
        self.away_team = match['c_AwayTeam_en']
        self.score = match['c_Score']
        self.match_id = match['n_MatchID']
        self.notifications = []

    def _notif_live(self):
        return "%s vs %s just started" % (self.home_team, self.away_team)

    def _notif_finish(self):
        return "%s vs %s finished %s" % (
            self.home_team, self.away_team, self.score)

    def _notif_score(self):
        return "%s vs %s goal! %s" % (
            self.home_team, self.away_team, self.score)

    @staticmethod
    def get_match_id(m):
        return m['n_MatchID']

    def update(self, match):
        live = match['b_Live']
        finished = match['b_Finished']
        score = match['c_Score']
        if live and live != self.live:
            self.notifications.append(self._notif_live())
            self.score = score
        self.live = live
        if finished and finished != self.finished:
            self.notifications.append(self._notif_finish())
        self.finished = finished
        if score != self.score:
            self.score = score
            if not finished:
                self.notifications.append(self._notif_score())

    def pop_notifications(self):
        ret = self.notifications
        self.notifications = []
        return ret


class Matches(object):
    URL = "http://live.mobileapp.fifa.com/api/wc/matches"

    def __init__(self):
        self.matches = {}
        dic = self._fetch()
        for m in dic:
            match = Match(m)
            self.matches[match.match_id] = match

    def _fetch(self):
        try:
            request = urllib2.Request(self.URL)
            response = urllib2.urlopen(request, None, 30)
            results = json.loads(response.read())
            return results["data"]["group"]
        except:
            return []

    def update(self):
        dic = self._fetch()
        for m in dic:
            match_id = Match.get_match_id(m)
            if match_id in self.matches:
                self.matches[match_id].update(m)
            else:
                self.matches[match_id] = Match(m)
        notifications = []
        for _, match in self.matches.iteritems():
            notifications += match.pop_notifications()
        if notifications:
            Slack.notify(notifications)
        else:
            cur_time = str(datetime.datetime.now())
            print "%s nothing changed (fetched %d)" % (cur_time, len(dic))


class Slack(object):
    URL = "http://localhost:8421/worldcup/goal"

    @staticmethod
    def _post(msg):
        try:
            data = {"message": msg}
            request = urllib2.Request(Slack.URL)
            urllib2.urlopen(request, urllib.urlencode(data), 30)
        except:
            pass

    @staticmethod
    def notify(msgs):
        # wait 60 before sending out notif
        time.sleep(60)
        for m in msgs:
            print m
            Slack._post(m)


if __name__ == '__main__':
    #Matches.URL = 'http://localhost:8597'
    matches = Matches()
    while True:
        time.sleep(15)
        matches.update()
