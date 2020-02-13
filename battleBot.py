#!/usr/bin/python

import re
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer

serv_ip = "172.22.115.228"
serv_port = 6667


def readWhois(input):
        print(input)


class battleBot(irc.IRCClient):
    nickname = "battleBot"
    chatroom = "#main"
    pattern = r'battleBot,\s+\b(\w*)\b\s+(.*)'
    challenges = []

    def signedOn(self):
        self.join(self.chatroom)


    def irc_RPL_WHOISUSER(self, *nargs):
        username = nargs[1][1]
        print ("Found user: " + username)
        self.foundNick = False

    def irc_RPL_ENDOFWHOIS(self, prefix, args):
        print(args)


    def isPresent(self, player):
        self.whois(player)
        return True


    def privmsg(self, user, channel, message):
        player = user.split("!")[0]
        with re.search(self.pattern, message) as regex:
            if regex is not None:
                if regex.group(1) == 'help':
                    self.describe(self.chatroom, 'commands: challenge <player>, yes, no')
                if regex.group(1) == 'challenge':
                    challengee = regex.group(2)
                    if self.isPresent(challengee):
                        self.describe(self.chatroom, '{} has been challenged! Do you accept?'.format(challengee))
                        challenge = {
                            "challenger": player,
                            "challengee": challengee
                        }
                        self.challenges.append(challenge)
                if regex.group(1) == 'yes':
                    for challenge in self.challenges:
                        if player in challenge.keys():
                            self.describe(self.chatroom, 'to battle!')
                            self.msg(challenge["challenger"], "you are the challenger")
                            self.msg(challenge["challengee"], "you are the challengee")
                if regex.group(1) == 'no':
                    self.describe(self.chatroom, '{} rejects the challenge'.format(challengee))
                    for challenge in self.challenges:
                        if player in challenge.keys():
                            self.challenges.remove(challenge)

# catch error for firing on the same spot or overlapping pieces
def main():
    f = protocol.ReconnectingClientFactory()
    f.protocol = battleBot

    reactor.connectTCP(serv_ip, serv_port, f)
    reactor.run()


if __name__ == "__main__":
    main()
