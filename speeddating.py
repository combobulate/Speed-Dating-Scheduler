'''
Created Wednesday Aug 21 2019

@author: Zefyr Scott

This code was designed to solve the problem of how to make a speed dating event
as inclusive as possible. Generally, straight speed dating events seat women each
at a table while men cycle to a new table for each round, while gay/lesbian and
bi/pan/queer dating events tend to use a round robin system. For a reasonably
diverse group of genders and gender preferences, it should still be possible to
apply the round robin system. The main problem (outside of all of the myriad other
compatibility factors) then becomes one of efficiency: unless nearly everyone is
bi/pan/queer, a decent amount of the pairing is devoted to connecting people who
are baseline incompatible for dating. The goal of this code is to make a maximally
efficient approach
'''

import re
import ast

class Person:
    def __init__(self, name, gender = 'N', dates_women = False, dates_men = False, dates_nonbinary = False):
        self.name = name
        self.gender = gender
        self.dates_women = dates_women
        self.dates_men = dates_men
        self.dates_nonbinary = dates_nonbinary
        
    def will_date(self, person):
        if ((self.dates_women and person.gender == 'F')
            or (self.dates_men and person.gender == 'M')
            or (self.dates_nonbinary and person.gender == 'X')):
            return True
        else: return False

class People:
    def __init__(self):
        self.peoplelist = []
    
    def add_person(self, person):
        self.peoplelist.append(person)
    
    def show_attendance(self, full_listing = False):
        for person in self.peoplelist:
            if(full_listing):
                print("Name: {} Gender: {} Dates women: {} Dates men: {} Dates nonbinary: {}"
                      .format(person.name, person.gender, person.dates_women, person.dates_men, person.dates_nonbinary))
            else:
                print("Name: ", person.name)
            
    def import_list(self, nextinputline):
        newitem = re.compile('[a-zA-Z]+')
        for line in nextinputline:
            nextinput = newitem.findall(line)
            name, gender, dates_women, dates_men, dates_nonbinary = nextinput
            self.peoplelist.append(Person(name, gender, ast.literal_eval(dates_women),
                                          ast.literal_eval(dates_men), ast.literal_eval(dates_nonbinary)))
        
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
            if (not (match.person_1.will_date(match.person_2) and match.person_2.will_date(match.person_1))):
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
            
    def assign_weights(self):
        validmatches = []
        for match in self.matchlist:
            if(match.valid): validmatches.append(match)

        for match in validmatches:
            weight = 0
            for othermatch in validmatches:
                if(self.match_overlap(match, othermatch)):
                    weight += 1
            match.weight = weight

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

    def get_next_table(self, minmax, tablelist):
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

    def schedule(self, people, tables = 'default'):
        if (tables == 'default'): tables = len(people.peoplelist) // 2
        
        minmaxlist = self.set_roundlist(people, tables, minmax = 'max', flip = True)
        minlist = self.set_roundlist(people, tables, minmax = 'min', flip = False)
        maxlist = self.set_roundlist(people, tables, minmax = 'max', flip = False)
        
        print('\nMinmax list: {} rounds'.format(len(minmaxlist)))
        self.show_schedule(minmaxlist)
        print('\nMin list: {} rounds'.format(len(minlist)))
        self.show_schedule(minlist)
        print('\nMax list: {} rounds'.format(len(maxlist)))
        self.show_schedule(maxlist)
        
        schedule = self.shortest_list(minlist, minmaxlist, maxlist)
        print('\nBest list: {} rounds'.format(len(schedule)))
        self.show_schedule(schedule)

    def shortest_list(self, *args):
        least = args[0]
        for arglist in args:
            if len(arglist) < len(least):
                least = arglist
        return least            

    def set_roundlist(self, people, tables, minmax = 'min', flip = False):
        self.remaining_matches, matches = self.valid_matches()
        roundlist = []
        matches_tabled = 0
        nexttable = None
        while(matches_tabled < matches):
            tablelist = []
            for table in range(tables):
                ### End of this loop may determine that no more tables can be
                ### seated this round without clashes, so check that first
                nexttable = self.get_next_table(minmax, tablelist)
                if(flip):
                    minmax = self.flip(minmax)
                    
                if (nexttable != 'none left'):
                    tablelist.append(nexttable)
                    self.remove_match(nexttable, self.remaining_matches)
                    matches_tabled += 1
                    
                if (nexttable == 'none left' or matches_tabled == matches): break

            nexttable = None ### Reset the variable for the next round
            roundlist.append(tablelist)
        return roundlist
            
    def show_schedule(self, roundlist):
        for a_round in range(len(roundlist)):
            print('======== Round {} ========'.format(a_round + 1))
            for match in range(len(roundlist[a_round])):
                print('Table {}: '.format(match + 1), end = '')
                roundlist[a_round][match].show_match()
