from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():

    return "Sent"

@app.route('/data', methods=['POST'])
def ml():
    import json
    if request.method == 'POST':
        data = request.get_data()
        json_ob = json.loads(data)

        from apyori import apriori
        from apyori import load_transactions

        orders = json_ob["orders"]

        class Recommender():
            def __init__(self, inputFile):
                self.AssociationRulesDictionary = {}  # holds final output
                self.dataFile = inputFile  # input datafile in csv form
                self.association_rules = []  # holds output from Apriori algo

            def computeRules(self):
                """
                Copmputes all association rules.
                :return:
                """
                with open(self.dataFile) as fileObj:
                    transactions = list(load_transactions(fileObj, delimiter=","))

                    # remove empty strings if any
                    transactions_filtered = []
                    a = set()

                    for li in transactions:
                        li = list(filter(None, li))
                        transactions_filtered.append(li)
                        a |= set(li)

                    self.association_rules = apriori(transactions_filtered, min_support=0.01, min_confidence=0.01,
                                                     min_lift=1.0,
                                                     max_length=None)

            def extractRules(self):

                for item in self.association_rules:

                    if len(item[0]) < 2:
                        continue

                    for k in item[2]:

                        baseItemList = list(k[0])
                        # if base item set is empty then go to the next record.
                        if not baseItemList:
                            continue

                        # sort the baseItemList before adding it as a key to the AssociationRules dictionary
                        baseItemList.sort()
                        baseItemList_key = tuple(baseItemList)

                        if baseItemList_key not in self.AssociationRulesDictionary.keys():
                            self.AssociationRulesDictionary[baseItemList_key] = []

                        self.AssociationRulesDictionary[baseItemList_key].append((list(k[1]), k[3]))

                # sort the rules in descending order of lift values.
                for ruleList in self.AssociationRulesDictionary:
                    self.AssociationRulesDictionary[ruleList].sort(key=lambda x: x[1], reverse=True)

            def recommend(self, itemList, Num=1):
                """
                itemList is a list of items selected by user
                Num is total recommendations required.
                :param item:
                :return:
                """

                # convert itemList to itemTuple as our dictionary key is a sorted tuple
                itemList.sort()
                itemTuple = tuple(itemList)

                if itemTuple not in self.AssociationRulesDictionary.keys():
                    return []

                return self.AssociationRulesDictionary[itemTuple][:Num]

            def studyRules(self):
                """
                This is a template method for computation and rule extraction.
                :return:
                """
                self.computeRules()
                self.extractRules()

        Biobuy = Recommender("my_new_csv.csv")
        Biobuy.studyRules()

        return str(Biobuy.recommend(orders, 3))



