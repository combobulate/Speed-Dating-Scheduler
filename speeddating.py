'''
Created Wednesday Aug 21 2019

@author: Zefyr Scott

This code was designed to solve the problem of how to make a speed dating event
both inclusive and diverse with regards to gender and sexual orientation.
Generally, straight speed dating events seat women each at a table while men 
cycle to a new table for each round, while gay/lesbian and bi/pan/queer dating
events tend to use a round robin system. For a reasonably diverse group of 
genders and gender preferences, it should still be possible to apply a round 
robin system. However, it may have efficiency problems: unless nearly everyone
is bi/pan/queer, a decent amount of the pairing is devoted to connecting 
people who are baseline incompatible for dating. This code applies a round 
robin system to make all possible matches, and then attempts to find an
efficient schedule for matches which are compatible based on gender and sexual
orientation.

To schedule matches, two weight methods are used.

    * In one, each match is given a weight based on how many other matches each
    person in the match has. IE if Bob matched with 10 people, and Joe matched
    with 12 people, the match of Bob and Joe has a weight of 21 (their match +
    Bob's 9 other matches + Joe's 11 other matches). This hopes to highlight
    matches on a more extreme end, where both members are either particularly busy
    or particularly not busy.
    
    * In the other, each match is given a weight based on its least busy member;
    in the above example, the match of Bob and Joe has a weight of 10. This hopes to highlig
    
Then some different methods are attempted to find an optimal schedule:
    
    * Tables for each round are filled based on finding lowest weight match
    where neither person for the match has been seated yet that round. This
    prioritizes finding a table for people who have the fewest options, and is
    intended to minimize situations where there are still available tables for
    the round but everyone who hasn't been seated yet has matches only with
    people who have already been seated that round. It also aims to help people
    with fewer matches have more back-to-back matches and finish up earlier.
    This is likely to work best when there are enough tables for everyone to sit
    each round.
    
    * Same approach, but seat from heighest weight match to lowest instead. This
    prioritizes finding a table for people who have the most options, and thus
    need to be seated the most times. When there are not enough tables for
    everyone to be seated each round, this is likely to do a better job of keeping
    seats full and finding the option with the fewest rounds.
    
    * Each time a new table is seated, switch between these two approaches. This
    attempts to find the best of both worlds, and may produce better results in
    some scenarios.

The schedule resulting in the fewest rounds is selected as the best schedule. If
there is a tie, each schedule is given a weight as the sum across all rounds of:
    (number of empty tables) * (number of rounds remaining including current round)
such that an empty table on the first of 10 rounds has a weight of 10, and an empty
table on the last of 10 rounds has a weight of 1. The schedule with the lowest
penalty sum is chosen.

Regarding gender and sexual orientation stuff: this is an effort at making
something both inclusive and widely accessible. However, orientation and identity
are complicated. In practice, nonbinary is an umbrella term for a lot of different
gender identities or lack thereof, as well as a gender identity. Many people who
identify as nonbinary also identify as men or women or both. How this is reflected
in the dating interests of their partners varies just as much. I opted to handle
gender as a pick-one-only option, and to treat nonbinary as a distinct gender
category. Participants should select whichever gender option they prefer to be
used for matching. Choosing nonbinary means only getting matched with people who
say they are interested in dating nonbinary people. The ability to select nonbinary
people as an interest for dating allows matching a user up with nonbinary people
exclusively.

There is a risk here that the programmatic ability to choose against dating
nonbinary people can be used as a tool of both nonbinaryphobia and transphobia.
Therefore, dates_nonbinary is True always, and gender interest options are
ideally presented as something like:
    * Interested in women (includes nonbinary people)
    * Interested in men (includes nonbinary people)
    * Interested in nonbinary people only
In the inevitable case of a mismatch because gender is complicated -- ie, someone
who identifies as both nonbinary and man is matched up with someone interested in
people who identify as both nonbinary and woman -- that can be considered a
similar 'mismatch' to that of, say, a feminine woman getting matched up with someone
only into masculine women.

'''

import re
import ast

class Person:
    def __init__(self, name, is_woman = False, is_man = False, is_nonbinary = False, dates_women = False, dates_men = False):
        self.name = name
        self.is_woman = is_woman
        self.is_man = is_man
        self.is_nonbinary = is_nonbinary
        self.dates_women = dates_women
        self.dates_men = dates_men
        self.dates_nonbinary = True
        
    def will_date(self, person):
        ## Abort if matched with round robin placeholder
        if (self.name == 'nobody' or person.name == 'nobody'): return False 
        ## If the active person is interested in a particular binary gender 
        ## matching the person of interest, go for it
        elif ((self.dates_women and person.is_woman)
                or (self.dates_men and person.is_man)):
            return True
        ## If the person of interest is not identified with one binary gender 
        ## only, match also. This handles the following cases as identical for 
        ## purposes of this sort of event. The third case may be a user input
        ## error or it may be someone's experience of something like bigender,
        ## which for purposes of this event is handled equivalently.
        ## is_nonbinary = True, is_woman = True, is_man = True
        ## is_nonbinary = True, is_woman = False, is_man = False
        ## is_nonbinary = False, is_woman = True, is_man = True
        elif ((person.is_man and person.is_woman) or
              ((not person.is_man) and (not person.is_woman))):
            return True
        ## If the active person is interested in nonbinary people only, the above
        ## cases will have missed someone who marked themself as nonbinary and
        ## also a single binary gender, so get them here.
        elif (person.is_nonbinary and ((not self.dates_women) and (not self.dates_men))):
            return True
        else: return False
    
    def show_person(self, full_listing = False):
        if(full_listing):
            gender = '  Gender: '
            if(self.is_woman): gender += 'woman, '
            if(self.is_man): gender += 'man, '
            if(self.is_nonbinary): gender += 'nonbinary, '
            gender = gender[:-2]
            
            dates = '  Dates: '
            if ((not self.dates_women) and (not self.dates_men)): dates += 'nonbinary people only'
            else:
                if(self.dates_women): dates += 'women, '
                if(self.dates_men): dates += 'men, '
                dates = dates[:-2] +  ' (incl. nonbinary)'
            
            print("Name: ", self.name, gender, dates)
            
        else:
            print("Name: ", self.name)

class People:
    def __init__(self):
        self.peoplelist = []
    
    def add_person(self, person):
        self.peoplelist.append(person)
    
    def show_attendance(self, full_listing = False):
        for person in self.peoplelist:
            person.show_person(full_listing)
            
    def import_list(self, nextinputline):
        newitem = re.compile('[a-zA-Z]+')
        for line in nextinputline:
            nextinput = newitem.findall(line)
            name, is_woman, is_man, is_nonbinary, dates_women, dates_men = nextinput
            self.peoplelist.append(Person(name, ast.literal_eval(is_woman), 
                    ast.literal_eval(is_man), ast.literal_eval(is_nonbinary), 
                    ast.literal_eval(dates_women), ast.literal_eval(dates_men)))
        
class Match:
    def __init__(self, person_1, person_2, weight = 0):
        self.person_1 = person_1
        self.person_2 = person_2
        self.weight = weight
        self.valid = True

    def show_match(self, display_invalid = False):
        if(display_invalid):
            if(self.person_1.name == 'nobody'):
                print(self.person_2.name, self.valid)
            elif(self.person_2.name == 'nobody'):
                print(self.person_1.name, self.valid)
            else:
                print(self.person_1.name, ' ', self.person_2.name, 'Match:', self.valid)  
        elif(self.valid):
            print(self.person_1.name, ' ', self.person_2.name, self.weight)  
        
class Matches:
    def __init__(self):
        self.matchlist = []
        self.remainingmatches = []
    
    def add_match(self, match):
        self.matchlist.append(match)

    def rotate(self, seats):
        return [seats[0], seats[-1]] + seats[1:-1]
              
    def make_matches(self, people):
        seats = people.peoplelist.copy()
        if(len(seats)%2 != 0):
            seats.append(Person('nobody'))
        for match_round in range(len(seats) - 1):
            for seat in range(len(seats) // 2):
                self.add_match( Match(seats[seat], seats[-(seat + 1)]) )
            seats = self.rotate(seats)

    def show_matches(self, display_invalid = False):
        for match in self.matchlist:
            match.show_match(display_invalid)

    def eliminate_false_matches(self):
        for match in self.matchlist:
            if ((not match.person_1.will_date(match.person_2)) or (not match.person_2.will_date(match.person_1))):
                match.valid = False

    def valid_matches(self):
        valid = []
        count = 0
        for match in self.matchlist:
            if(match.valid):
                valid.append(match)
                count += 1
        return valid, count

    def match_overlap(self, match1, match2):
        if('nobody' in (match1.person_1.name, match1.person_2.name)
            and 'nobody' in (match2.person_1.name, match2.person_2.name)):
            return False
        elif(match1.person_1.name == match2.person_1.name
            or match1.person_1.name == match2.person_2.name
            or match1.person_2.name == match2.person_1.name
            or match1.person_2.name == match2.person_2.name):
            return True
        else: return False
            
    def assign_weights_net(self):
        validmatches = []
        for match in self.matchlist:
            if(match.valid): validmatches.append(match)

        for match in validmatches:
            weight = 0
            for othermatch in validmatches:
                if(self.match_overlap(match, othermatch)):
                    weight += 1
            match.weight = weight
    
    def assign_weights_min(self):
        validmatches = []
        for match in self.matchlist:
            if(match.valid): validmatches.append(match)

        for match in validmatches:
            weight1 = 0
            weight2 = 0
            for othermatch in validmatches:
                if(match.person_1 in (othermatch.person_1, othermatch.person_2)):
                    weight1 += 1
                if(match.person_2 in (othermatch.person_1, othermatch.person_2)):
                    weight2 += 1
            match.weight = min(weight1, weight2)

    def assign_weights_max(self):
        validmatches = []
        for match in self.matchlist:
            if(match.valid): validmatches.append(match)

        for match in validmatches:
            weight1 = 0
            weight2 = 0
            for othermatch in validmatches:
                if(match.person_1 in (othermatch.person_1, othermatch.person_2)):
                    weight1 += 1
                if(match.person_2 in (othermatch.person_1, othermatch.person_2)):
                    weight2 += 1
            match.weight = max(weight1, weight2)

    def minweight(self, previous = None):
        lowest = [Match(Person('nobody'), Person('nobody'), weight = 1000)]
        for match in self.remaining_matches:
            if (previous):
                
                ### If previous tables no good, we need a match with a higher
                ### weight. If the currently assigned lowest is not higher, take
                ### current match and it'll be tested in the next loop.

                if (lowest[0].weight <= previous[0].weight):
                    lowest = [match]
                
                ### Otherwise the latest picked match hasn't been tried yet. See
                ### if the next match in the list is valid too.
                elif (match.weight > previous[0].weight):
                    
                    ### If yes and it's less than the latest picked, replace latest
                    if (match.weight < lowest[0].weight):
                        lowest = [match]
                
                    ### If yes and it's equal to the latest picked, add to latest
                    elif (match.weight == lowest[0].weight):
                        lowest += [match]
            
            else:
                
                ### If it's less than the latest picked, replace latest
                if (match.weight < lowest[0].weight):
                    lowest = [match]
            
                ### If it's equal to the latest picked, add to latest
                elif (match.weight == lowest[0].weight):
                    lowest += [match]
                        
        if(lowest[0].weight == 1000):
            lowest = None
            
        return lowest

    def maxweight(self, previous = None):
        highest = [Match(Person('nobody'), Person('nobody'), weight = 0)]
        for match in self.remaining_matches:
            if (previous):
                
                ### If previous tables no good, we need a match with a lower
                ### weight. If the currently assigned lowest is not lower, take
                ### current match and it'll be tested in the next loop.

                if (highest[0].weight >= previous[0].weight):
                    highest = [match]
                
                ### Otherwise the latest picked match hasn't been tried yet. See
                ### if the next match in the list is valid too.
                elif (match.weight < previous[0].weight):
                    
                    ### If yes and it's greater than the latest picked, replace latest
                    if (match.weight > highest[0].weight):
                        highest = [match]
                
                    ### If yes and it's equal to the latest picked, add to latest
                    elif (match.weight == highest[0].weight):
                        highest += [match]
            
            else:
                
                ### If match is greater than the latest picked, replace latest
                if (match.weight > highest[0].weight):
                    highest = [match]
            
                ### If it's equal to the latest picked, add to latest
                elif (match.weight == highest[0].weight):
                    highest += [match]
                        
        if(highest[0].weight == 0):
            highest = None
            
        return highest
        
    def nextweight(self, minmax, **kwargs):
        if (minmax == 'min'):
            return self.minweight(**kwargs)
        else: return self.maxweight(**kwargs)

    def flip(self, minmax):
        if (minmax == 'min'):
            return 'max'
        else: return 'min'
            
    def remove_match(self, delmatch, matchlist):
        for match in matchlist:
            if (match == delmatch):
                matchlist.remove(match)
                break

    def get_next_match(self, minmax, tablelist):
        nexttable = None
        
        ### Grab the tables with the lowest weight, and mark an empty spot
        sometables = self.nextweight(minmax)
        
        ### If no one is seated already, seat the first table retrieved
        if (len(tablelist) == 0): nexttable = sometables[0]
        
        ### Otherwise, let's check against already filled tables for clashes.
        while (not nexttable):
            for sometable in sometables:
                clash = False
                for filledtable in tablelist:
                    if(self.match_overlap(sometable, filledtable)):
                        clash = True
                
                if(not clash):
                    nexttable = sometable
                    break
                    
            ### If we still haven't found anything, try the next up weights
            if (not nexttable):
                sometables = self.nextweight(minmax, previous = sometables)

                ### We might run out of matches before tables so get out of the loop
                if (not sometables): nexttable = 'none left'

        return nexttable
    
    def efficiency_check(self, schedules, tables):
        minpenalty = None
        best = schedules[0]
        
        for schedule in schedules:
            penalty = 0
            for i, a_round in enumerate(schedule):
                penalty += (tables - len(a_round)) * (len(schedule) - i)
            if(minpenalty):
                if minpenalty > penalty:
                    best = schedule
                    minpenalty = penalty
            else: minpenalty = penalty
                    
        return best
            

    def schedule(self, people, tables = 'default'):
        if (tables == 'default'): tables = len(people.peoplelist) // 2
        
        schedules = []
        self.assign_weights_max()
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = False))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = False))
        self.assign_weights_min()
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = False))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = False))
        self.assign_weights_net()
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = True))
        schedules.append(self.set_roundlist(people, tables, minmax = 'min', flip = False))
        schedules.append(self.set_roundlist(people, tables, minmax = 'max', flip = False))
        
        #print('\nMinmax list: {} rounds'.format(len(minmaxlist)))
#        self.show_schedule(minmaxlist)
#        print('\nMin list: {} rounds'.format(len(minlist)))
#        self.show_schedule(minlist)
#        print('\nMax list: {} rounds'.format(len(maxlist)))
#        self.show_schedule(maxlist)
        
        schedule = self.shortest_list(schedules)
        if (len(schedule) == 1):
            best = schedule[0]
        else:
            best = self.efficiency_check(schedule, tables)

        print('\nBest option: {} rounds'.format(len(best)))
        self.show_schedule(best)

    def shortest_list(self, schedules):
        least = [schedules[0]]
        for schedule in schedules:
            if (len(schedule) < len(least[0])):
                least = [schedule]
            elif (schedule is not least[0]):
                if (len(schedule) == len(least[0])):
                    least += [schedule]
        return least

    def set_roundlist(self, people, tables, minmax = 'min', flip = False):
        self.remaining_matches, matches = self.valid_matches()
        roundlist = []
        matches_tabled = 0
        nextmatch = None
        while(matches_tabled < matches):
            tablelist = []
            for table in range(tables):
                ### End of this loop may determine that no more tables can be
                ### seated this round without clashes, so check that first
                nextmatch = self.get_next_match(minmax, tablelist)
                if(flip):
                    minmax = self.flip(minmax)
                    
                if (nextmatch != 'none left'):
                    tablelist.append(nextmatch)
                    self.remove_match(nextmatch, self.remaining_matches)
                    matches_tabled += 1
                    
                if (nextmatch == 'none left' or matches_tabled == matches): break

            nextmatch = None ### Reset the variable for the next round
            roundlist.append(tablelist)
        return roundlist
            
    def show_schedule(self, roundlist):
        for a_round in range(len(roundlist)):
            print('======== Round {} ========'.format(a_round + 1))
            for match in range(len(roundlist[a_round])):
                print('Table {}: '.format(match + 1), end = '')
                roundlist[a_round][match].show_match()
