import random
from typing import Callable

def findAnyInSet(source: set, predicate: Callable[..., bool]):
    try:
        return random.choice([item for item in source if predicate(item)])
    except IndexError:
        return None
    
def findFirstInSet(source: set, predicate: Callable[..., bool]):
    return next(iter({item for item in source if predicate(item)}), None)

def findAllInSet(source: set, predicate: Callable[..., bool]) -> set:
    return {item for item in source if predicate(item)}

class IdentifierGenerator:
    def __init__(self, seed: str):
        self.SEED = seed
        random.seed(seed)

    def getIdentifier(self) -> str:
        return str(random.randint(0, 20000))


class Rule:
    def __init__(self, identifier: str, firstToken: str, followingToken: str, isTerminal: bool = False, isInitial: bool = False):
        self.isTerminal = isTerminal
        self.isInitial = isInitial
        self.identifier = identifier
        self.firstToken = firstToken
        self.followingToken = followingToken

    def generate(self, rules: set):
        if (self.isTerminal):
            return self.firstToken
        else: 
            return findAnyInSet(rules, lambda rule: rule.identifier == self.firstToken).generate(rules) + ((findAnyInSet(rules, lambda rule: rule.identifier == self.followingToken).generate(rules)) if (not self.isTerminal) else '')


def formatRule(rule: Rule) -> str:
    return f'{rule.identifier} {"i" if rule.isInitial else ""}{"t" if rule.isTerminal else ""}-> ({rule.firstToken}, {rule.followingToken})'

def formatRules(rules) -> str:
    return list(map(lambda rule: formatRule(rule), rules))


class Grammar:
    def __init__(self, identifierGenerator: IdentifierGenerator, rules: set = set()):
        self.__ig = identifierGenerator
        self.__rules = rules

    def generate(self, count:int) -> list[str]:
        generated = []

        for i in range(count):
            initialRule = findAnyInSet(self.__rules, lambda rule: rule.isInitial == True)
            if (initialRule is not None):
                generated.append(initialRule.generate(self.__rules))
            else:
                break

        return generated

    def teachExact(self, inputStr: str):

        inputStrIter = iter(inputStr)
        currentChar = next(inputStrIter, None)
        nextChar = next(inputStrIter, None)
        isInitial = True
        currentRuleIdentifier = self.__ig.getIdentifier()
        nextRuleIdentifier = self.__ig.getIdentifier()
        currentRule = None

        while(currentChar is not None):

            if (currentChar is not None):

                terminalRule = findFirstInSet(self.__rules, lambda rule, currentChar = currentChar: (rule.isTerminal == True) and (rule.firstToken == currentChar))
                if (terminalRule is None):
                    terminalIdentifier = self.__ig.getIdentifier()
                    terminalRule = Rule(
                        identifier = terminalIdentifier, 
                        firstToken= currentChar, 
                        followingToken= None, 
                        isTerminal= True,
                        isInitial= False
                        )
                    print('creating Rule', formatRule(terminalRule))
                    self.__rules.add(terminalRule)

                # currentRule = terminalRule

                if (nextChar is not None):
                    currentRule = findFirstInSet(self.__rules,\
                        lambda rule, terminalRule = terminalRule: (rule.isTerminal == False)\
                            and (rule.firstToken == terminalRule.identifier)\
                            and ((rule.identifier == currentRuleIdentifier) \
                                or ((isInitial == True) and (rule.isInitial == True)) )
                            )
                    if (currentRule is None):
                        currentRule = Rule(
                            identifier= currentRuleIdentifier, 
                            firstToken= terminalRule.identifier, 
                            followingToken= nextRuleIdentifier, 
                            isTerminal= False,
                            isInitial= isInitial
                            )
                        print('creating Rule', formatRule(currentRule))
                        self.__rules.add(currentRule)
                    else:
                        print('reused Rule', formatRule(currentRule))
                        nextRuleIdentifier = currentRule.followingToken
                else:
                    if (currentRule is not None):
                        # at least one rule is created 
                        # setting followingToken for previous rule to be the terminal rule of the last char not generated identifier
                        if (findFirstInSet(self.__rules, lambda rule, followingToken = previousRule.followingToken: rule.identifier == followingToken) is None):
                            print(f'followingToken of previousRule ({currentRule.identifier}) is set to {terminalRule.identifier}')
                            previousRule.followingToken = terminalRule.identifier
                        else:
                            currentRule = Rule(
                                identifier= previousRule.identifier, 
                                firstToken= previousRule.firstToken, 
                                followingToken= terminalRule.identifier, 
                                isTerminal= False,
                                isInitial= previousRule.isInitial
                                )
                            print('creating ending Rule', formatRule(currentRule))
                            self.__rules.add(currentRule)
                    else:
                        #happens when single char word appears and no initial rules have been created
                        terminalRule.isInitial = True

            isInitial = False
            previousRule = currentRule
            currentRuleIdentifier = nextRuleIdentifier
            nextRuleIdentifier = self.__ig.getIdentifier()
            currentChar = nextChar
            nextChar = next(inputStrIter, None)


    def getDuplicatedRules(self) -> list[Rule]:
        iterator = iter(self.__rules)
        
        firstRule = next(iterator, None)
        while (firstRule is not None):
            secondRule = findFirstInSet(self.__rules, lambda secondRule, firstRule = firstRule: (secondRule.identifier != firstRule.identifier) and (secondRule.firstToken == firstRule.firstToken) and (secondRule.followingToken == firstRule.followingToken) and (secondRule.isInitial == firstRule.isInitial))
            if secondRule is not None:
                print('found duplicated rules', formatRules([firstRule, secondRule]))
                return [firstRule, secondRule]

            firstRule = next(iterator, None)
        return []

    def mergeDuplicatedRules(self, rule1, rule2):
        print('removing duplicated rule', formatRules([rule1]))
        for rule in self.__rules:
            if (rule != rule1):
                
                if (rule.identifier == rule1.identifier):
                    rule.identifier = rule2.identifier

                if (rule.firstToken == rule1.identifier):
                    rule.firstToken = rule2.identifier

                if (rule.followingToken == rule1.identifier):
                    rule.followingToken = rule2.identifier
        
        self.__rules.remove(rule1)
        del rule1

    def mergeAllDuplicatedRules(self):
        print('rules before mergeAllDuplicatedRules', formatRules(self.__rules))
        isMerged = True
        while (isMerged):
            isMerged = False

            duplicatedRules = self.getDuplicatedRules()
            if (len(duplicatedRules) != 0):
                isMerged = True 
                self.mergeDuplicatedRules(duplicatedRules[0], duplicatedRules[1])
        
        print('rules after mergeAllDuplicatedRules', formatRules(self.__rules))


    def teach(self, inputStrs: list[str]):
        inputStrs.sort(reverse=True, key=len)
        for inputStr in inputStrs:
             self.teachExact(inputStr)
        self.mergeAllDuplicatedRules()

separator = ' '

with open('translation.txt', 'r') as file:
    data = file.read().replace('\n', '')


inputStrings = data.split(separator)
grammar = Grammar(IdentifierGenerator('1'))
grammar.teach(inputStrings)

with open('output.txt', 'w') as file:
    file.write(' '.join(grammar.generate(30)))