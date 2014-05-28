'''
Created on Mar 14, 2014

Jednostavni ekspertni sustav.

@author: Viktor Berger
'''
import Eparser

############################################################################################
#                                    POMOCNE FUNKCIJE                                      #
############################################################################################

# funkcija vraca string s pravilom u formatu lakom za citanje,
# odnosno:  IF condition THEN action 
def rule_repr(rule):
    LHS = []
    for attr,values in rule['LHS'].items():
        LHS.append(attr + " = " + "|".join(values))
        
    (RHSkey,RHSvalue) = rule['RHS'].items()[0]
    
    return "IF " + " & ".join(LHS) + " THEN " + RHSkey + " = " + RHSvalue

# Funkcija ispisuje radnu memoriju
def printRM():
    print "Radna memorija:"
    for r,v in RM.items():
        print r, " = ", v

# Funkcija vraca listu svih konfliktnih pravila, odnosno pravila cija desna strana 
# izvodi vrijednost danog parametra
def getConflictRules(rules,goal):
    ruleset = []
    for rule in rules:
        attribute = rule['RHS'].keys()[0]
        if attribute == goal:
            ruleset.append(rule)            
    return ruleset

# Funkcija provjerava postoji li barem jedno pravilo cija desna strana 
# izvodi vrijednost danog cilja
def conflictRuleExists(rules,goal):
    for rule in rules:
        attribute = rule['RHS'].keys()[0]
        if attribute == goal:
            return True        
    return False


# Funkcija provjerava da li dano pravilo pali
# Drugim rijecima, ako su svi atributi s lijeve strane pravila u 
# radnoj memoriji i imaju jednake vrijednosti
def ruleWorks(rule,RM):
    conditions = rule['LHS']
    
    for param in conditions:
        if param in RM:
            if RM[param] not in conditions[param]:
                return False
        else:
            return False
    return True

# Funkcija za korisnicki unos zadanog parametra u radnu memoriju
# Zahtjeva unos dok korisnik ne unese jedan od dopustenih vrijednosti
# Napomena: korisnicki unos moguc je samo za parametre cije ime zavrsava sa znakom '*' 
def parameterInput(param,RM):
    value = raw_input("Molim unesite vrijednost parametra '" + param + "' " + str(parameters[param+"*"]))
    while(value not in parameters[param+"*"]):
        value = raw_input()
    RM[param] = value
    
    
# Funkcija ispisuje atribute/parametre, njihove vrijednosti
# i sva pravila sadrzana u bazi znanja
def printKnowledgeBase(parameters,rules):
    print '-'*105 
    print '|' + '\t'*6 + 'BAZA ZNANJA' + '\t'*6 + '|'
    print '-'*105 + '\n'
    
    print "Atributi:"
    for attr,value in parameters.items():
        print attr + " = " + " | ".join(value)
    
    print "\nPravila:"
    for i,rule in enumerate(rules):
        print str(i+1) + ") " + rule_repr(rule)
        
    print '-'*105 + '\n'
        

############################################################################################
#                                    GLAVNI PROGRAM                                        #
############################################################################################
# dohvati atribute i pravila iz baze znanja
parameters, rules = Eparser.parse('../base/zivotinje.txt')

# ispisi bazu znanja
printKnowledgeBase(parameters, rules)

# radna memorija, stog s ciljevima i lista vec provjerenih atributa
# cija se vrijednost ne moze izvesti
RM = {}
goals = []
checked_goals = []


# Oblikuj stog inicijalno sastavljen od najvaznijih ciljeva(hipoteza) koje treba dokazati

# Zatrazi korisnika unos ciljne hipoteze
goal = raw_input('Unesi hipotezu: ')
goals.append(goal)

# Na vrhu stoga je hipoteza koju treba dokazati.Ako je stog prazan, onda je KRAJ

# Glavna petlja
while(True):
    
    # ako je stog prazan, izadi iz petlje
    if len(goals) == 0:
        break
    
    # pomocne kontrolne varijable
    new_goal = False
    new_parameter = False 
    
    # pohrani trnutni cilj u varijablu goal
    goal = goals[-1]
 
    # stvori skup konfliktnih pravila i pohrani njihov broj
    conflictRules = getConflictRules(rules,goal)
    remainingRules = len(conflictRules)
    
    # ako nije pronadeno nijedno konfliktno pravilo prekini petlju i obavijesti korisnika
    if remainingRules == 0:
        print 'Premalo podataka'
        break
    
    # ispisi skup konfliktnih pravila i stanje radne memorije
    print 'Konfliktna pravila: '
    for cr in conflictRules:
        print rule_repr(cr)
    printRM()
    
    # U petlji prolazi kroz skup konfliktnih pravila      
    # Ako pravilo pali:
    # 1) skini trenutni cilj s vrha stoga
    # 2) pohrani njegovu desnu stranu u radnu memoriju
    # 3) postavi varijablu new_goal u True i izadi iz petlje
    for cr in conflictRules:
        if ruleWorks(cr,RM):
            (RHSkey,RHSvalue) = cr['RHS'].items()[0]
            RM[RHSkey] = RHSvalue
            curr_goal = goals.pop()
            print "Ostvaren je cilj: "  + curr_goal + " = " + RHSvalue
            new_goal = True
            break
    
    # Ako je idi na iduci cilj
    if new_goal:
        continue   
        
    # za svako pravilo u skupu konfliktnih pravila
    for cr in conflictRules:
        
        # ako je new_goal True, izadji iz petlje
        if new_goal :
            break
        
        # smanji broj preostalih neprovjerenih pravila
        remainingRules -= 1
        conditions = cr['LHS']
        
        # za svaki parametar pravila koje se trenutno provjerava
        for param in conditions:
            # ako je parametar vec provjeren i nije ga bilo moguce izvesti, 
            # preskoci pravilo (ne provjeravaj ostale parametre )
            if param in checked_goals:
                break
            # ako je trenutni parametar u radnoj memoriji
            if param in RM:
                # vrijednost parametra se ne podudara s vrijednoscu koja je u radnoj memoriji
                if RM[param] not in conditions[param]:
                    break
            else: # parametar nije u memoriji
                # ako neko od pravila izvodi trenutni parametar, postavi ga za cilj
                if conflictRuleExists(rules,param): 
                    goals.append(param)
                    new_goal = True
                    break                
                elif param + "*" in parameters: 
                    # Nijedno od pravila ne izvodi parametar 
                    # ako je moguce(ime parametra zavrsava sa znakom '*'), 
                    # trazi korisnika za unos vrijednosti parametra
                    parameterInput(param,RM)
                    new_parameter = True
                    break
                else:
                    # parametar se ne moze izvesti iz nekog od pravila i 
                    # korisnik ga ne moze unesti
                    checked_goals.append(param)
        
        # ako je unesen novi parametar, ponovno provjeri pravila (izadji iz petlje)
        if new_parameter:
            break
                    
        # ako nije postavljen novi cilj i sva su pravila provjerena, skini cilj s vrha stoga
        # i pohrani ga u listu ciljeva koji se ne mogu ostvariti
        if remainingRules == 0 and not new_goal:
            curr_goal = goals.pop()
            checked_goals.append(curr_goal)
            print 'Neostvarivi cilj: ' + curr_goal
            
    print '-'*100
                    
                    
print '*'*48 + "KRAJ RADA" + '*'*48
                    
    
    
    