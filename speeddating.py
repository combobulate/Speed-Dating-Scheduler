# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 20:03:30 2019

@author: HP
"""

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
        self.personal_schedule = []
        
    def will_date(self, person):
        ## Abort if matched with round robin placeholder
        if ('nobody' in (self.name, person.name)): return False 
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

    def show_personal_schedule(self):
        print("\nName: ", self.name)
        for i in self.personal_schedule:
            print(i)
            
class People:
    def __init__(self):
        self.people_list = []
    
    def add_person(self, person):
        self.people_list.append(person)
    
    def show_attendance(self, full_listing = False):
        for person in self.people_list:
            person.show_person(full_listing)
    
    ### Use for importing from text file. Expects each line to be an alpha-only
    ### name followed by six booleans
    def import_list(self, nextinputline):
        newitem = re.compile('[a-zA-Z]+')
        for line in nextinputline:
            nextinput = newitem.findall(line)
            name, is_woman, is_man, is_nonbinary, dates_women, dates_men = nextinput
            self.people_list.append(Person(name, ast.literal_eval(is_woman), 
                    ast.literal_eval(is_man), ast.literal_eval(is_nonbinary), 
                    ast.literal_eval(dates_women), ast.literal_eval(dates_men)))

class Match:
    def __init__(self, person_1, person_2):
        self.person_1 = person_1
        self.person_2 = person_2
        self.valid = True
        self.lowerweight = 0
        self.higherweight = 0

    def show_match(self, display_invalid = False, display_weights = False):
        if(display_invalid): ## this is for troubleshooting
            if(self.person_1.name == 'nobody'):
                print(self.person_2.name, self.valid)
            elif(self.person_2.name == 'nobody'):
                print(self.person_1.name, self.valid)
            else:
                print(self.person_1.name, ' ', self.person_2.name, 'Match:', self.valid)  
        elif(self.valid):
            if (display_weights): ## this is for troubleshooting
                print(self.person_1.name, ' ', self.person_2.name, self.lowerweight, self.higherweight)  
            else:
                print(self.person_1.name, ' ', self.person_2.name)    
    
    ## Compares two matches and returns true if someone is in both
    def overlap(self, match):
        if(self.person_1.name in (match.person_1.name, match.person_2.name)
            or self.person_2.name in (match.person_1.name, match.person_2.name)):
            return True
        else: return False
                
class Matches:
    def __init__(self):
        self.matchlist = []
    
    def add_match(self, match):
        self.matchlist.append(match)
        
    def rotate(self, seats):
    ## Used for round robin matching
        return [seats[0], seats[-1]] + seats[1:-1]        

    def make_matches(self, people):
    ## Round robin matching
        seats = people.people_list.copy()
        if(len(seats)%2 != 0):
            seats.append(Person('nobody'))
        for match_round in range(len(seats) - 1):
            for seat in range(len(seats) // 2):
                self.add_match(Match(seats[seat], seats[-(seat + 1)]))
            seats = self.rotate(seats)

    def show_matches(self, display_invalid = False):
        for match in self.matchlist:
            match.show_match(display_invalid)

    ## Deactivate any match where one or both members would not date the other
    ## due to gender
    def eliminate_false_matches(self):
        for match in self.matchlist:
            if ((not match.person_1.will_date(match.person_2))
                or (not match.person_2.will_date(match.person_1))):
                match.valid = False

    ## Returns list of all valid matches from the object's matchlist                
    def valid_matches(self):
        valid = []
        for match in self.matchlist:
            if(match.valid):
                valid.append(match)
        return valid
    
    ## Sets weights for each match. Each person in the match is checked for total
    ## number of matches. The lower number is set as lowerweight, the higher is
    ## higherweight.
    def assign_weights(self):
        validmatches = self.valid_matches()

        for match in validmatches:
            weight1 = 0
            weight2 = 0
            for othermatch in validmatches:
                if(match.person_1 in (othermatch.person_1, othermatch.person_2)):
                    weight1 += 1
                if(match.person_2 in (othermatch.person_1, othermatch.person_2)):
                    weight2 += 1
            match.lowerweight = min(weight1, weight2)
            match.higherweight = max(weight1, weight2)
    
    ## Returns list of valid matches sorted by weight
    def sort_by_weights(self):
        
        ## Make a temp version of the valid matches so we can safely delete stuff
        tempmatches = Matches()
        tempmatches.matchlist = self.valid_matches()
        
        ## Make a new list of the matches in weight order
        sortedmatches = []
        
        nextmatch = tempmatches.get_next_match()
        
        while(nextmatch):
            sortedmatches.append(nextmatch)
            nextmatch = tempmatches.get_next_match()
            
        del tempmatches
        return sortedmatches
    
    ## Gets next match by weight, for sort_by_weights
    def get_next_match(self):
        if(self.matchlist):
            lowest = self.matchlist[0]
            
            for match in self.matchlist:
                ## If it's less than the latest picked, replace latest
                if (match.lowerweight < lowest.lowerweight):
                    lowest = match
            
                ## If it's equal to the latest picked, check the higherweight.
                ## We want matches with lowest lowerweight and highest higherweight
                elif (match.lowerweight == lowest.lowerweight):
                    
                    ## If there's a match with equal lowerweight and higher
                    ## higherweight, replace latest
                    if (match.higherweight > lowest.higherweight):
                        lowest = match
                    
            if(lowest):
                self.remove_match(lowest)
            
            return lowest
        
        else: return None

    ## Gets next match from list which is assumed to be sorted, for set_rounds
    def seat_next_match(self, tables):
        nexttable = None
        
        while(not nexttable):
            ## For each match in the sorted list of matches: see if anyone in
            ## that match is already seated this round. If yes, the next match
            ## in the list will be attempted. Otherwise, seat that match.
            for match in self.matchlist:
                clash = False
                for table in tables:
                    if (match.overlap(table)):
                        clash = True
                        break
                
                if (not clash):
                    nexttable = match
                    self.remove_match(match)
                    break
            if (not nexttable):
                nexttable = 'None left'
        return nexttable
            
    ## Removes a match from a list
    def remove_match(self, delmatch):
        self.matchlist.remove(delmatch)

class Schedule:
    def __init__(self):
        self.rounds = []

    def set_rounds(self, tables, people, matches):
        remaining_matches = Matches()
        remaining_matches.matchlist = matches.sort_by_weights()
        self.rounds = []
        while(remaining_matches.matchlist):
            a_round = []
            for table in range(tables):
                nextmatch = remaining_matches.seat_next_match(a_round)
                if(nextmatch != 'None left'):
                    a_round.append(nextmatch)
                else: break
            self.rounds.append(a_round)
        self.sort_rounds()
    
    def sort_rounds(self):
        sortedrounds = []
        while(self.rounds):
            biggest = self.biggest_round()
            sortedrounds.append(biggest)
            self.rounds.remove(biggest)
        self.rounds = sortedrounds
        
    def biggest_round(self):
        biggest = self.rounds[0]
        for a_round in self.rounds:
            if (len(a_round) > len(biggest)):
                biggest = a_round
        
        return biggest
    
    def show_rounds(self):
        for a_round in range(len(self.rounds)):
            print('======== Round {} ========'.format(a_round + 1))
            for match in range(len(self.rounds[a_round])):
                print('Table {}: '.format(match + 1), end = '')
                self.rounds[a_round][match].show_match()
                
class Scheduler:
    def __init__(self):
        pass

    ## This function carries most of the weight once a list of people is loaded.
    ## Default number of tables is the maximum which can be filled by the total
    ## number of complete matches, valid or not.
    def make_schedule(self, people, tables = 'default'):
        if (tables == 'default'): tables = len(people.people_list) // 2
        elif (tables > len(people.people_list) // 2): tables = len(people.people_list) // 2
        
        matches = Matches()
        matches.make_matches(people)
        matches.eliminate_false_matches()
        matches.assign_weights()
        
        most_tables, efficient_tables = self.best_options(tables, people, matches)
        print('\nMost tables early on option: {} rounds, {} tables'.format(len(most_tables.rounds), len(most_tables.rounds[0])))
        most_tables.show_rounds()
        
        print('\nPersonal schedules for max tables option:')
        self.make_individual_schedules(most_tables, people)
        self.show_individual_schedules(people)

        print('\nMost table efficient option: {} rounds, {} tables'.format(len(efficient_tables.rounds), len(efficient_tables.rounds[0])))
        efficient_tables.show_rounds()

        print('\nPersonal schedules for efficiency option:')
        self.make_individual_schedules(efficient_tables, people)
        self.show_individual_schedules(people)

    ## Gets best option for each number of tables up through the total number
    ## available
    def best_options(self, tables, people, matches):
        options = []
        
        ## Get baseline best option for each number of tables
        for numtables in range(tables, 2, -1):
            ## Only try this number of tables if it hasn't been done already;
            ## a previous run may not have been able to use all available tables
            if ((len(options) == 0) or (len(options[-1].rounds[0]) > numtables)):
                options.append(self.table_option(numtables, people, matches))
        
        ## First grab the schedule for the specified table count. It 
        ## is possible that it will not be able to use all tables. It may be
        ## desirable to use this schedule and not do all rounds.
        shortest = options[0]
        
        ## Next, see if another schedule is as short and has better table usage.
        ## It may be worth using fewer tables and getting all the rounds in.
        efficient_tables = self.shortest_schedule(options)[-1]

        return shortest, efficient_tables
    
    def table_option(self, *args):
        schedule = Schedule()
        schedule.set_rounds(*args)
        return schedule
    
    def shortest_schedule(self, schedules):
        ## Returns list of all shortest schedules from a list of schedules
        least = [schedules[0]]
        for sch in schedules:
            if (len(sch.rounds) < len(least[0].rounds)):
                least = [sch]
            elif (sch is not least[0]):
                if (len(sch.rounds) == len(least[0].rounds)):
                    least += [sch]

        return least

    def make_individual_schedules(self, schedule, people):
        for person in people.people_list:
            person.personal_schedule = []
            
        for i, a_round in enumerate(schedule.rounds):
            for j, table in enumerate(a_round):
                table.person_1.personal_schedule.append("Round {}: Table {}".format(i + 1, j + 1))
                table.person_2.personal_schedule.append("Round {}: Table {}".format(i + 1, j + 1))
    
    def show_individual_schedules(self, people):
        for person in people.people_list:
            person.show_personal_schedule()