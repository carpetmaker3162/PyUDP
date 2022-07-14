from src.PyUDP import Unit
import time

if __name__ == "__main__":
    t = time.time()
    latency = time.time() - t
    
    t = time.time()
    unit1 = Unit("nerd cat")
    unit2 = Unit("cat")
    unit3 = Unit("kasli the scourge")
    unit4 = Unit("mecha-bun")
    unit5 = Unit("jurassic cat")
    unit6 = Unit("lasvoss")
    print(f"Loading in 6 Unit objects took {time.time() - t - latency:.4f}s (1/2, by name)")

    t = time.time()
    assert Unit(UID=35).name == "Nerd Cat"
    assert Unit(UID=0).name == "Cat"
    assert Unit(UID=529).name == "Kasli the Scourge"
    assert Unit(UID=426).name == "Mecha-Bun"
    assert Unit(UID=46).name == "Jurassic Cat"
    assert Unit(UID=519).name == "Lasvoss"
    print(f"Loading in 6 Unit objects took {time.time() - t - latency:.4f}s (2/2, by UID)")
    assert unit1.id == 35
    assert unit2.id == 0
    assert unit3.id == 529
    assert unit4.id == 426
    assert unit5.id == 46
    assert unit6.id == 519
    print("ID/Name GET test: Passing")
    
    assert unit1.upgrade(30) == 4285850
    assert unit1.upgrade(10, 20) == 1430700
    assert unit2.upgrade(43, 47) == 31200
    assert unit4.upgrade(1, 48) == 11770450
    print("XP curve test:    Passing")

    assert unit1.catcombos == {"IT Crowd - Accounting Power UP (Sm)": ["260", "035"]}
    assert unit2.catcombos == {'Cat Army - Worker Cat Start Level UP (Sm)': ['000', '001', '002', '003', '004'], "Mo' Hawks - Knockback Effect UP (Sm)": ['000', '098'], 'Smiles at Cats - Freeze Effect UP (Sm)': ['000', '107'], 'Rich and Poor - Starting Money UP (Sm)': ['000', '129'], 'Black & White - Worker Cat Max UP (Sm)': ['319', '000']}
    assert unit3.catcombos == {'None': []}
    assert unit4.catcombos == {'None': []}
    assert unit5.catcombos == {'Age of Dinosaurs - Cat Base Defense UP (Sm)': ['007', '046'], 'Mini-Saurus - Research Power UP (Sm)': ['209', '046']}
    assert unit6.catcombos == {'Bad Guys - Research Power UP (L)': ['519', '172', '319']}
    print("Combos test:      Passing")

    assert unit1.tf_requirements == {'XP': '500000', 'GREEN_CATFRUIT': '2', 'PURPLE_CATFRUIT': '2', 'RED_CATFRUIT': '2', 'BLUE_CATFRUIT': '2', 'EPIC_CATFRUIT': '1'}
    assert unit2.tf_requirements == {}
    assert unit3.tf_requirements == {}
    assert unit4.tf_requirements == {'XP': '1000000', 'GREEN_CATFRUIT_SEED': '5', 'BLUE_CATFRUIT_SEED': '5', 'YELLOW_CATFRUIT_SEED': '5', 'EPIC_CATFRUIT': '10', 'ELDER_CATFRUIT': '1'}
    assert unit5.tf_requirements == {'XP': '200000', 'PURPLE_CATFRUIT_SEED': '3', 'BLUE_CATFRUIT_SEED': '2', 'YELLOW_CATFRUIT_SEED': '3', 'GREEN_CATFRUIT': '1', 'RED_CATFRUIT': '1'}
    assert unit6.tf_requirements == {'XP': '1000000', 'EPIC_CATFRUIT_SEED': '10', 'ELDER_CATFRUIT': '1', 'GOLD_CATFRUIT': '1'}
    print("TF reqs test:     Passing")
    
    assert unit1.talents == {'Slow Duration': 9.41, 'Survives': 6.75, 'Barrier Breaker': 1.9, 'Attack Buff': 0.8, 'Cost Down': 2.44}
    assert unit2.talents == {}
    assert unit3.talents == {}
    assert unit4.talents == {}
    assert unit5.talents == {'Critical Chance': 8.79}
    assert unit6.talents == {}
    print("Talents test:     Passing")